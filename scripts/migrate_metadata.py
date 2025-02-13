import os
import re
import yaml
from pathlib import Path


def find_schema_files(schema_dir: str = 'tushare_integration/schema') -> list[str]:
    """查找所有schema文件"""
    schema_files = []
    for root, _, files in os.walk(schema_dir):
        for file in files:
            if file.endswith('.yaml') and file != '__init__.py':
                schema_files.append(os.path.join(root, file))
    return schema_files


def get_model_path(schema_path: str) -> str:
    """根据schema文件路径获取对应的model文件路径"""
    # 从schema路径中提取API名称
    api_name = os.path.splitext(os.path.basename(schema_path))[0]
    return f'tushare_integration/models/{api_name}.py'


def read_schema_metadata(schema_path: str) -> tuple[list[str], list[str]]:
    """读取schema文件中的元数据"""
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = yaml.safe_load(f)

    # 处理dependencies，只保留路径的最后一部分
    dependencies = schema.get('dependencies', [])
    dependencies = [dep.split('/')[-1] for dep in dependencies] if dependencies else []

    primary_key = schema.get('primary_key', [])

    return dependencies, primary_key


def update_model_file(model_path: str, dependencies: list[str], primary_key: list[str]) -> None:
    """更新model文件中的元数据"""
    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        return

    with open(model_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 更新dependencies
    content = re.sub(
        r'__dependencies__: ClassVar\[List\[str\]\] = \[.*?\]',
        f'__dependencies__: ClassVar[List[str]] = {dependencies}',
        content,
        flags=re.DOTALL,
    )

    # 更新primary_key
    content = re.sub(
        r'__primary_key__: ClassVar\[List\[str\]\] = \[.*?\]',
        f'__primary_key__: ClassVar[List[str]] = {primary_key}',
        content,
        flags=re.DOTALL,
    )

    with open(model_path, 'w', encoding='utf-8') as f:
        f.write(content)


def main():
    # 确保目录存在
    schema_dir = 'tushare_integration/schema'
    if not os.path.exists(schema_dir):
        print(f"Schema directory not found: {schema_dir}")
        return

    # 查找所有schema文件
    schema_files = find_schema_files(schema_dir)
    print(f"Found {len(schema_files)} schema files")

    # 处理每个schema文件
    for schema_path in schema_files:
        try:
            print(f"\nProcessing {schema_path}")

            # 获取对应的model文件路径
            model_path = get_model_path(schema_path)

            # 读取schema元数据
            dependencies, primary_key = read_schema_metadata(schema_path)

            # 更新model文件
            update_model_file(model_path, dependencies, primary_key)

            print(f"Updated {model_path}")
            print(f"Dependencies: {dependencies}")
            print(f"Primary Key: {primary_key}")

        except Exception as e:
            print(f"Error processing {schema_path}: {str(e)}")


if __name__ == '__main__':
    main()
