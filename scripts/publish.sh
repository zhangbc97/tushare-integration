#!/bin/bash

# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建包
python -m build

# 检查构建的包
twine check dist/*

# 上传到PyPI
if [ "$1" = "--test" ]; then
    echo "Uploading to TestPyPI..."
    twine upload --repository testpypi dist/*
else
    echo "Uploading to PyPI..."
    twine upload dist/*
fi 