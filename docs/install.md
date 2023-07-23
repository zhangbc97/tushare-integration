# 安装

## Kubernetes部署(Helm)

    cd deploy/tushare-integration
    helm install tushare-integration ./ -f values.yaml

### 基于CronJob的定时任务

values.yaml中包含cronjob字段用于配置定时任务，可根据自己需求进行修改

## 使用Docker

    docker pull zhangbc/tushare-integration:latest

## 直接使用源码

### 从仓库获取源码

    git clone git@github.com:zhangbc97/tushare-integration.git

#### 使用pip安装依赖

    pip install -r requirements.txt

#### 使用poetry安装依赖

    pip install poetry
    poetry install