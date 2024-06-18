import pathlib

import yaml


def get_type_default(data_type: str) -> str:
    match data_type:
        case 'str':
            return ''
        case 'int':
            return '0'
        case 'float':
            return '0.0'
        case 'number':
            return '0.0'
        case 'datetime':
            return '1971-01-01 00:00:00'
        case 'date':
            return '1971-01-01'
        case 'json':
            return ''
        case _:
            raise ValueError(f'Unknown data type: {data_type}')


def parse_schema(schema: dict):
    v2_schema = {
        'id': schema['id'],
        'api_name': schema['name'],
        'name': schema['name'],
        'comment': schema['title'],
        'dependencies': schema.get('dependencies', []),
        'columns': [],
    }
    # 先把所有的output字段转换成新的格式

    if 'outputs' in schema:
        for output in schema['outputs']:
            v2_schema['columns'].append(
                {
                    'name': output['name'],
                    'data_type': output['data_type'],
                    'length': 255 if output['data_type'] == 'str' else 0,
                    'default': get_type_default(output['data_type']),
                    'comment': output['desc'],
                }
            )

    return v2_schema


def main():
    # 将旧版本的schema文件转换成新版
    # 遍历tushare_integration/schema下的所有.yaml文件，包括他的子目录，转换后输出到tushare_integration/schema_v2下

    schema_dir = pathlib.Path(__file__).parent / 'tushare_integration' / 'schema'

    print(schema_dir)

    for schema_file in schema_dir.rglob('*.yaml'):
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema = yaml.safe_load(f)

        schema = parse_schema(schema)

        schema_v2_file = (
            pathlib.Path(__file__).parent / 'tushare_integration' / 'schema_v2' / schema_file.relative_to(schema_dir)
        )
        schema_v2_file.parent.mkdir(parents=True, exist_ok=True)
        with open(schema_v2_file, 'w', encoding='utf-8') as f:
            f.write(yaml.safe_dump(schema, allow_unicode=True, default_flow_style=False, sort_keys=False))


if __name__ == '__main__':
    main()
