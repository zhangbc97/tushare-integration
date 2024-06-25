#!/bin/bash
set -ex
# 模块名
MODULE_NAME=tushare-integration

# 版本号，从命令行传入
VERSION=$1

# 镜像名
IMAGE=registry.cn-beijing.aliyuncs.com/ai-labs/${MODULE_NAME}:${VERSION}

# Dockerfile
DOCKERFILE=Dockerfile

docker build --build-arg=PIP_SOURCE=https://pypi.tuna.tsinghua.edu.cn/simple -f ${DOCKERFILE} -t ${IMAGE} .

docker push ${IMAGE}

cmd /k