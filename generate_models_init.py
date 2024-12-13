import importlib.util
import inspect
import os
import sys
from pathlib import Path
from typing import List, Tuple

from jinja2 import Environment, FileSystemLoader


def get_classes_from_module(module_name: str, module_path: Path) -> List[str]:
    """获取模块中所有的类"""
    # 添加项目根目录到 Python 路径，以便正确导入
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    try:
        # 使用 importlib 导入模块
        spec = importlib.util.spec_from_file_location(module_name, str(module_path))
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot import module {module_name} from {module_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module  # 添加到 sys.modules 以支持循环导入
        spec.loader.exec_module(module)

        classes = []
        for name, obj in inspect.getmembers(module):
            # 只获取定义在当前模块中的类（排除导入的类）
            if inspect.isclass(obj) and obj.__module__ == module_name and not name.startswith('_'):  # 排除内部类
                classes.append(name)
        return classes

    except Exception as e:
        print(f"Warning: Could not process {module_path.name}: {str(e)}")
        return []


def generate_models_init():
    # 获取项目根目录和models目录的路径
    root_dir = Path(__file__).parent
    models_dir = root_dir / 'tushare_integration' / 'models'

    if not models_dir.exists():
        raise FileNotFoundError(f"Models directory not found at {models_dir}")

    # 获取所有.py文件
    py_files = []
    for file in sorted(os.listdir(models_dir)):
        if file.endswith('.py') and file != '__init__.py':
            module_name = file[:-3]  # 移除.py后缀
            module_path = models_dir / file
            classes = get_classes_from_module(module_name, module_path)
            if classes:  # 只添加包含类的模块
                py_files.append((module_name, classes))

    # 创建jinja2环境
    env = Environment(loader=FileSystemLoader(root_dir), trim_blocks=True, lstrip_blocks=True)

    # 创建模板
    template_str = '''# This file is auto-generated. Do not edit it manually.

{% for module, classes in modules %}
from .{{ module }} import {{ classes|join(', ') }}
{% endfor %}

__all__ = [
    {% for module, classes in modules %}
    {% for class_name in classes %}
    '{{ class_name }}',
    {% endfor %}
    {% endfor %}
]
'''

    template = env.from_string(template_str)

    # 渲染模板
    output = template.render(modules=py_files)

    # 写入文件
    init_path = models_dir / '__init__.py'
    with open(init_path, 'w', encoding='utf-8') as f:
        f.write(output)

    print(f"Generated __init__.py with {len(py_files)} modules")
    if len(py_files) == 0:
        print("Warning: No classes were found in any modules")


if __name__ == '__main__':
    generate_models_init()
