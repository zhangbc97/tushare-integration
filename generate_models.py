import ast
import logging
import os
import re
from typing import Any, Dict, List

import requests
from jinja2 import StrictUndefined, Template

cookie = ''
# SQLAlchemy模型模板
MODEL_TEMPLATE = '''from sqlalchemy import Column, text
from clickhouse_sqlalchemy import engines
from typing import ClassVar, Dict, Any, List

from tushare_integration.models.core import String, Integer, Float, Date, DateTime, Base


class {{ table_name|to_camel_case }}(Base):
    """{{ table_comment }}"""

    __tablename__: str = '{{ table_name }}'
    __api_id__: ClassVar[int] = {{ api_id }}
    __api_name__: ClassVar[str] = '{{ api_name }}'
    __api_title__: ClassVar[str] = '{{ api_title }}'
    __api_info_title__: ClassVar[str] = '{{ api_info_title }}'
    __api_path__: ClassVar[List[str]] = {{ api_path }}
    __api_path_ids__: ClassVar[List[int]] = {{ api_path_ids }}
    __api_points_required__: ClassVar[int] = {{ api_points_required }}
    __api_special_permission__: ClassVar[bool] = {{ api_special_permission }}
    __dependencies__: ClassVar[List[str]] = {{ dependencies if dependencies is defined else [] }}
    __primary_key__: ClassVar[List[str]] = {{ primary_key }}
    __start_date__: ClassVar[str | None] = {{ start_date if start_date is defined else None }}
    __end_date__: ClassVar[str | None] = {{ end_date if end_date is defined else None }}
    __api_params__: ClassVar[Dict[str, Any]] = {{ api_params }}
    
    __mapper_args__ = {'primary_key': __primary_key__}
    __table_args__ = (
        # ClickHouse引擎
        engines.ReplacingMergeTree(order_by=__primary_key__),
        {
            'comment': '{{ table_comment }}',
            # MySQL引擎
            'mysql_engine': 'InnoDB',
            # StarRocks引擎
            'starrocks_primary_key': ','.join(__primary_key__),
            'starrocks_order_by': ','.join(__primary_key__),
            # Apache Doris引擎
            'doris_unique_key': __primary_key__,
        }
    )
    {% for field in fields %}
    {{ field.name }} = Column('{{ field.original_name }}', {{ field|get_column_type }}, nullable=False, default={{ field.default|tojson }}, server_default=text({{ field|get_server_default }}), comment='{{ field.comment }}')
    {%- endfor %}
'''


def get_default_by_data_type(data_type: str):
    """
    根据数据类型获取默认值

    Args:
        data_type: 数据类型

    Returns:
        对应的默认值

    Raises:
        ValueError: 当数类型未知或为空时
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


def escape_quote(text: str | None) -> str:
    """
    转���字符串中的引号将中文括号替换为英文括号

    Args:
        text: 需要处理的字符串

    Returns:
        处理后的字符串
    """
    if text is None:
        return ''
    # 先替换括号，再处理引号
    text = text.replace("（", "(").replace("）", ")")  # 替换中文括号为英文括号
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
        return []  # 返回空列表而不是 None

    fields = api_info['data']['outputs']
    for field in fields:
        original_name = field['name'].lower()

        # 处理以数字开头的字段名 - 只修改Python变量名，保留原始列名
        if original_name[0].isdigit():
            field['original_name'] = original_name  # 保存原始列名
            field['name'] = f"_{original_name}"  # Python变量名加下划线
        # 处理Python关键字 - 只修改Python变量名，保留原始列名
        elif is_python_keyword(original_name):
            field['original_name'] = original_name  # 保存原始列名
            field['name'] = f"_{original_name}"  # Python变量名加下划线
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
    将下划线形式转换为峰命名

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
            # 只ts_code字段才指定具体长度，其他用空括号
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


def get_primary_key(fields: List[Dict[str, Any]]) -> List[str]:
    """
    确定表的主键字段

    规则:
    1. 如果同时存 ts_code 和 trade_date，使用它作为联合主键
    2. 其他情况返回空列表

    Args:
        fields: 字段列表

    Returns:
        主键字段列表
    """
    field_names = [field['original_name'] for field in fields]

    if 'ts_code' in field_names and 'trade_date' in field_names:
        return ['ts_code', 'trade_date']
    return []


def get_api_params(api_info: dict) -> Dict[str, Any]:
    """从API信息中获取输入参数配置"""
    if not api_info or 'data' not in api_info or 'inputs' not in api_info['data']:
        return {}

    params = {}
    for param in api_info['data']['inputs']:
        params[param['name']] = {
            'type': param.get('data_type', 'str'),
            'required': param.get('must', 'N').upper() == 'Y',
            'description': param.get('desc', ''),
        }
    return params


def get_document_tree():
    """获取API文档树结构"""
    url = 'https://tushare.pro/wctapi/documents/tree'
    response = requests.get(url, headers={'Cookie': cookie})
    if response.status_code != 200:
        raise Exception(f'获取文档树失败，状态码: {response.status_code}')

    if response.json()['code'] != 0:
        logging.warning(f'获取文档树失败，错误信息: {response.json()["message"]}')
        return None
    return response.json()['data']


def build_api_title_map(tree_data: List[Dict]) -> Dict[int, Dict[str, Any]]:
    """从文档树构建API信息映射"""
    info_map = {}

    def traverse_tree(node, parent_titles: List[str] | None = None, parent_ids: List[int] | None = None):
        if parent_titles is None:
            parent_titles = []
        if parent_ids is None:
            parent_ids = []

        current_title = node.get('title', '')
        current_id = node.get('id', 0)
        current_path = parent_titles + [current_title]
        current_path_ids = parent_ids + ([current_id] if current_id != 0 else [])

        if 'id' in node:
            info_map[current_id] = {
                'title': current_title,
                'desc': node.get('desc', ''),
                'parent_ids': parent_ids,
                'path': current_path,
                'path_ids': current_path_ids,
                'category': parent_titles[0] if parent_titles else '',
                'api_name': node.get('api_name', ''),
                'points_required': 2000,
                'special_permission': False,
            }

        if 'children' in node and node['children']:
            for child in node['children']:
                traverse_tree(child, current_path, current_path_ids)

    for category in tree_data:
        traverse_tree(category)

    return info_map


def print_document_tree(tree_data: List[Dict], level: int = 0):
    """
    打印文档树结构

    Args:
        tree_data: 文档树数据
        level: 当前层级（用于缩进）
    """
    for node in tree_data:
        indent = "  " * level
        title = node.get('title', '')
        api_name = node.get('api_name', '')
        print(f"{indent}{'├─' if level > 0 else ''} {title} {f'({api_name})' if api_name else ''}")

        if 'children' in node and node['children']:
            print_document_tree(node['children'], level + 1)


# 在文件顶部添加全局变量
_API_TITLE_MAP: Dict[int, Dict[str, Any]] | None = None


def get_api_title_map() -> Dict[int, Dict[str, Any]]:
    """
    获取并缓存API标题映射

    Returns:
        Dict[int, Dict[str, Any]]: API ID到信息的映射，包含标题、父ID列表和路径
    """
    global _API_TITLE_MAP

    if _API_TITLE_MAP is None:
        doc_tree = get_document_tree()
        if doc_tree is not None:
            # 打印文档树结构
            logging.info("文档树结构：")
            print_document_tree(doc_tree)

            _API_TITLE_MAP = build_api_title_map(doc_tree)
            logging.info(f"成功获取 {len(_API_TITLE_MAP)} 个API的标题��息")

            # 打印标题映射结果
            logging.info("API标题映射：")
            for api_id, info in sorted(_API_TITLE_MAP.items()):
                logging.info(
                    f"{api_id}: {info['title']} (父ID: {info['parent_ids']}, 路径: {' > '.join(info['path'])})"
                )
        else:
            logging.error("无法获取文档树，将使用原始标题")
            _API_TITLE_MAP = {}

    return _API_TITLE_MAP


def extract_class_attributes(file_path: str) -> Dict[str, Any]:
    """
    从现有模型文件中提取类属性值

    Args:
        file_path: 模型文件路径

    Returns:
        包含提取出的属性值的字典
    """
    if not os.path.exists(file_path):
        return {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用正则表达式匹配类属性定义
        patterns = {
            'api_points_required': r'__api_points_required__:\s*ClassVar\[int\]\s*=\s*(\d+)',
            'api_special_permission': r'__api_special_permission__:\s*ClassVar\[bool\]\s*=\s*(True|False)',
            'dependencies': r'__dependencies__:\s*ClassVar\[List\[str\]\]\s*=\s*(\[.*?\])',
            'primary_key': r'__primary_key__:\s*ClassVar\[List\[str\]\]\s*=\s*(\[.*?\])',
            'start_date': r'__start_date__:\s*ClassVar\[str\s*\|\s*None\]\s*=\s*(\'.*?\'|\".*?\"|None)',
            'end_date': r'__end_date__:\s*ClassVar\[str\s*\|\s*None\]\s*=\s*(\'.*?\'|\".*?\"|None)',
        }

        result = {}
        for attr, pattern in patterns.items():
            match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
            if match:
                value_str = match.group(1)
                try:
                    # 使用ast.literal_eval安全地解析Python字面值
                    result[attr] = ast.literal_eval(value_str)
                except (ValueError, SyntaxError):
                    logging.warning(f"无法解析{attr}的值: {value_str}")

        return result

    except Exception as e:
        logging.error(f"从文件{file_path}提取属性时发生错误: {str(e)}")
        return {}


def generate_model(api_id: int, output_dir: str):
    """
    生成SQLAlchemy模型文件

    Args:
        api_id: API ID
        output_dir: 输出目录
    """
    logging.info(f"开始处理 API ID: {api_id}")

    api_info = get_api_info(api_id)
    if api_info is None:
        logging.error(f"无法获取API {api_id}的信息")
        return

    api_name = api_info['data']['name']
    output_path = os.path.join(output_dir, f"{api_name}.py")

    # 提取现有文件中的属性
    existing_attrs = extract_class_attributes(output_path)

    # 获取API标题和路径信息
    api_info_map = get_api_title_map()
    tree_info = api_info_map.get(
        api_id,
        {
            'title': api_info['data']['title'],
            'desc': api_info['data'].get('desc', ''),
            'parent_ids': [],
            'path': [api_info['data']['title']],
            'path_ids': [],
            'category': '',
            'points_required': 2000,
            'special_permission': False,
        },
    )

    fields = get_fields(api_info)
    if fields is None:
        logging.error(f"无法获取API {api_id}的字段信息")
        return

    # 准备模板变量时优先使用现有文件中的值
    template_vars = {
        'table_name': api_name,
        'fields': fields,
        'table_comment': escape_quote(tree_info['title']),
        'api_id': api_id,
        'api_name': api_info['data']['name'],
        'api_title': escape_quote(tree_info['title']),
        'api_info_title': escape_quote(api_info['data']['title']),
        'api_path': tree_info.get('path', [api_info['data']['title']]),
        'api_path_ids': tree_info.get('path_ids', []),
        'api_points_required': existing_attrs.get('api_points_required', tree_info.get('points_required', 0)),
        'api_special_permission': existing_attrs.get(
            'api_special_permission', tree_info.get('special_permission', False)
        ),
        'primary_key': existing_attrs.get('primary_key', get_primary_key(fields)),
        'api_params': get_api_params(api_info),
    }

    # 添加可选属性（只在存在时添加）
    if 'dependencies' in existing_attrs:
        template_vars['dependencies'] = existing_attrs['dependencies']
    if 'start_date' in existing_attrs:
        template_vars['start_date'] = repr(existing_attrs['start_date'])  # 使用 repr 确保字符串正确引用
    if 'end_date' in existing_attrs:
        template_vars['end_date'] = repr(existing_attrs['end_date'])  # 使用 repr 确保字符串正确引用

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

    # 这里生成的模型文件必须确认好主键后再使用，这里默认生成的主键不一定正确
    # 目前最大的ID是358，留点冗余
    # for i in range(1, 400):
    #     generate_model(api_id=i, output_dir='tushare_integration/models')

    generate_model(api_id=355, output_dir='tushare_integration/models')
