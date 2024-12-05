import logging
import os
from typing import Any, Dict, List

import requests
from jinja2 import StrictUndefined, Template

cookie = ''
# SQLAlchemy模型模板
MODEL_TEMPLATE = '''from sqlalchemy import Column, text

from tushare_integration.models.base import Base, String, Integer, Float, Date, DateTime


class {{ table_name|to_camel_case }}(Base):
    """{{ table_comment }}"""

    __tablename__ = '{{ table_name }}'
    __api_id__ = {{ api_id }}
    __api_name__ = '{{ api_name }}'

    {% for field in fields %}
    {% if field.name[0].isdigit() %}
    _{{ field.name }} = Column('{{ field.original_name }}', {{ field|get_column_type }}, nullable=False, default={{ field.default|tojson }}, server_default=text({{ field|get_server_default }}), comment='{{ field.comment }}')
    {%- else %}
    {{ field.name }} = Column('{{ field.original_name }}', {{ field|get_column_type }}, nullable=False, default={{ field.default|tojson }}, server_default=text({{ field|get_server_default }}), comment='{{ field.comment }}')
    {%- endif %}
    {%- endfor %}

    __table_args__ = {
        'comment': '{{ table_comment }}'
    }
'''


def get_default_by_data_type(data_type: str):
    """
    根据数据类型获取默认值

    Args:
        data_type: 数据类型

    Returns:
        对应的默认值

    Raises:
        ValueError: 当数据类型未知或为空时
    """
    if data_type is None:
        raise ValueError("data_type is None")

    match data_type.lower():
        case "str" | "varchar":
            return ""
        case "float" | "number" | "double":
            return 0.0
        case "int" | "bigint":
            return 0
        case "date":
            return "1970-01-01"
        case "datetime" | "timestamp":
            return "1970-01-01 00:00:00"
        case "json":
            return '{}'
        case _:
            raise ValueError(f"Unsupported data_type: {data_type}")


def get_api_info(api_id: int):
    url = f'https://tushare.pro/wctapi/documents/{api_id}/api_info'
    response = requests.get(url, headers={'Cookie': cookie})
    if response.status_code != 200:
        raise Exception(f'获取 API 息失败，状态码: {response.status_code}')

    if response.json()['code'] != 0:
        logging.warning(f'获取 API 信息失败错误信息: {response.json()["message"]}')
        return None
    return response.json()


def escape_quote(text: str) -> str:
    """
    转义字符串中的引号
    
    Args:
        text: 需要转义的字符串
    
    Returns:
        转义后的字符串
    """
    return text.replace("'", "\\'").replace('"', '\\"')


def is_python_keyword(name: str) -> bool:
    """
    检查是否是Python关键字
    
    Args:
        name: 需要检查的名称
    
    Returns:
        是否是Python关键字
    """
    import keyword
    return keyword.iskeyword(name)


def get_fields(api_info: dict) -> List[Dict[str, Any]]:
    """
    从API信息中获取字段信息
    """
    if api_info is None:
        return None

    fields = api_info['data']['outputs']
    for field in fields:
        original_name = field['name'].lower()
        
        # 处理Python关键字 - 只修改Python变量名，保留原始列名
        if is_python_keyword(original_name):
            field['original_name'] = original_name  # 保存原始列名
            field['name'] = f"_{original_name}"    # Python变量名加下划线
        else:
            field['original_name'] = original_name
            field['name'] = original_name

        # 特殊处理ts_code字段
        if original_name == 'ts_code':
            field['length'] = 16

        # 处理日期相关字段
        if original_name.endswith('_date'):
            field['data_type'] = 'date'

        # 处理data_type为空的情况
        if field['data_type'] is None or field['data_type'] == '':
            field['data_type'] = 'str'

        field['default'] = get_default_by_data_type(field['data_type'])
        field['comment'] = escape_quote(field.pop('desc'))

    return fields


def to_camel_case(snake_str: str) -> str:
    """
    将下划线形式转换为驼峰命名

    Args:
        snake_str: 下划线形式的字符串

    Returns:
        驼峰命名形式的字符串
    """
    components = snake_str.split('_')
    return ''.join(x.title() for x in components)


def get_column_type(field: Dict[str, Any]) -> str:
    """
    根字段类型返回对应的SQLAlchemy列类型

    Args:
        field: 字段信息字典

    Returns:
        SQLAlchemy列类型字符串

    Raises:
        ValueError: 当字段类型未知时
    """
    data_type = field['data_type'].lower() if field['data_type'] else 'str'

    match data_type:
        case "str" | "varchar":
            # 只有ts_code字段才指定具体长度，其他使用空括号
            return f"String({field['length']})" if field.get('length') else "String()"
        case "float" | "number" | "double":
            return 'Float'
        case "int" | "bigint":
            return 'Integer'
        case "datetime" | "timestamp":
            return 'DateTime'
        case "date":
            return 'Date'
        case "json":
            return "String()"  # JSON类型使用空括号
        case _:
            raise ValueError(f"Unsupported data_type: {data_type} for field {field['name']}")


def get_server_default(data_type: str, value: Any) -> str:
    """
    根据数据类型生成server_default的文本值

    Args:
        data_type: 数据类型
        value: 默认值

    Returns:
        格式化后的server_default文本
    """
    match data_type.lower():
        case "str" | "varchar" | "json":
            return f'"\'{ value }\'"'
        case "float" | "number" | "double" | "int" | "bigint":
            return f'"\'{ value }\'"'
        case "date" | "datetime" | "timestamp":
            return f'"\'{ value }\'"'
        case _:
            raise ValueError(f"Unsupported data_type: {data_type}")


def generate_model(api_id: int, output_dir: str):
    """
    生成SQLAlchemy模型文件

    Args:
        api_id: API ID
        output_dir: 输出目录路径
    """
    logging.info(f"开始处理 API ID: {api_id}")

    api_info = get_api_info(api_id)
    if api_info is None:
        logging.error(f"无法获取API {api_id}的信息")
        return

    api_name = api_info['data']['name']
    api_title = api_info['data']['title']
    logging.info(f"正在处理: [{api_id}] {api_title} ({api_name})")

    fields = get_fields(api_info)
    if fields is None:
        logging.error(f"无法获取API {api_id}的字段信息")
        return
    logging.info(f"成功获取字段信息， {len(fields)} 个字段")

    # 使用 api_name 作为表名和文件名
    table_name = api_name
    output_path = os.path.join(output_dir, f"{table_name}.py")

    # 准备模板变量时转义表注释
    template_vars = {
        'table_name': table_name,
        'fields': fields,
        'table_comment': escape_quote(api_info['data']['title']),
        'api_id': api_id,
        'api_name': api_info['data']['name'],
    }

    # 创建Jinja2环境并添加过滤器
    env = Template.environment_class(undefined=StrictUndefined)
    env.filters['to_camel_case'] = to_camel_case
    env.filters['get_column_type'] = get_column_type
    env.filters['get_server_default'] = lambda f: get_server_default(f['data_type'], f['default'])

    # 使用环境创建模板
    template = env.from_string(MODEL_TEMPLATE)
    output = template.render(**template_vars)

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 写入文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(output)

    logging.info(f"成功生成模型文件: {output_path}")
    logging.info("=" * 50)


if __name__ == '__main__':
    # 配置日志格式
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )

    # for i in range(1, 1000):
    # generate_model(api_id=i, output_dir='tushare_integration/models')

    generate_model(api_id=201, output_dir='tushare_integration/models')
