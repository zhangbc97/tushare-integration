import os
import shutil
import sys
from pathlib import Path

def clean():
    """清理旧的构建文件"""
    print("清理旧的构建文件...")
    paths = ['dist', 'build', '*.egg-info']
    for path in paths:
        for p in Path('.').glob(path):
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()

def build():
    """构建包"""
    print("构建包...")
    os.system(f"{sys.executable} -m build")

def check():
    """检查构建的包"""
    print("检查构建的包...")
    os.system(f"{sys.executable} -m twine check dist/*")

def upload(test=False):
    """上传到PyPI"""
    if test:
        print("上传到TestPyPI...")
        os.system(f"{sys.executable} -m twine upload --repository testpypi dist/*")
    else:
        print("上传到PyPI...")
        os.system(f"{sys.executable} -m twine upload dist/*")

def main():
    clean()
    build()
    check()
    
    # 检查命令行参数
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        upload(test=True)
    else:
        upload()

if __name__ == '__main__':
    main() 