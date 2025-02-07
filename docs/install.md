# 安装

## Kubernetes部署(Helm)

    cd deploy/tushare-integration
    helm install tushare-integration ./ -f values.yaml

### 基于CronJob的定时任务

values.yaml中包含cronjob字段用于配置定时任务，可根据自己需求进行修改，参考[配置文档](settings.md)

## 使用Docker

    docker pull zhangbc/tushare-integration:latest

## 通过PyPI安装

建议您为项目创建虚拟环境以避免依赖冲突，例如：

    python3 -m venv env
    source env/bin/activate

然后从PyPI安装最新版本的 tushare-integration：

- 使用清华大学镜像站：
    
    pip install -i https://pypi.tuna.tsinghua.edu.cn/simple tushare-integration

- 或使用默认源：
    
    pip install tushare-integration

## 直接使用源码

### 从仓库获取源码

    git clone git@github.com:zhangbc97/tushare-integration.git

#### 使用pip安装依赖

    pip install -r requirements.txt

#### 使用uv管理依赖
    pip install uv
    uv install

# 升级

根据您使用的安装方式，选择相应的升级方法：

## Docker方式升级

    docker pull zhangbc/tushare-integration:latest

## PyPI方式升级

    pip install --upgrade tushare-integration

## Kubernetes (Helm)方式升级

    helm upgrade tushare-integration ./ -f values.yaml

## 直接使用源码升级

1. 拉取最新代码：
    
       cd tushare-integration
       git pull

2. 更新依赖：
    
       pip install -r requirements.txt
       uv install