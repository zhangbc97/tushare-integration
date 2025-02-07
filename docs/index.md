# 项目介绍

## 项目背景

Tushare Pro目前已稳定运行几年时间，其提供了大量的金融数据接口，不过Tushare Pro接口在使用过程中有频次限制，在数据分析过程中，我们希望能够不受限制的访问数据库，
因此需要在每日更新后，将数据同步到本地数据库中。Tushare Integration就是为了解决这个问题而生。

## 项目目标

- 实现同步 Tushare Pro 接口数据到本地数据库，并支持全量同步与增量更新
- 支持将数据写入到多种数据库

## 快速开始

### 前置条件

- Python 3.8+
- Docker（推荐）或本地数据库环境
- Tushare Pro 账号及 Token（[注册地址](https://tushare.pro/register?reg=7)）
- 至少2000积分以上的账号（推荐5000分以上）

### 使用Docker快速部署（推荐）

1. 拉取并运行Clickhouse容器

```bash
docker pull clickhouse/clickhouse-server:23.6.2.18-alpine
docker run -d --name clickhouse-server \
    --net=host \
    -v /data/clickhouse:/var/lib/clickhouse \
    --ulimit nofile=262144:262144 \
    clickhouse/clickhouse-server:23.6.2.18-alpine
```

2. 创建配置文件

```bash
mkdir -p /data/tushare-integration/config
```

3. 编写基础配置文件 (config.yaml)

```yaml
tushare_token: '你的Token'  # 替换为你的Token
tushare_point: 2000        # 替换为你的积分

database:
  db_type: 'clickhouse'
  host: '127.0.0.1'
  port: '8123'
  user: 'default'
  password: ''
  db_name: 'default'
```

4. 运行数据同步任务

```bash
docker run -d --net=host \
    -v /data/tushare-integration/config/config.yaml:/code/app/config.yaml \
    zhangbc/tushare-integration:latest \
    python main.py run spider stock/basic/stock_basic
```

### 验证安装

1. 检查数据是否写入成功

```sql
SELECT count(*) FROM stock_basic;
```

2. 查看最新同步数据

```sql
SELECT * FROM stock_basic ORDER BY list_date DESC LIMIT 5;
```

### 下一步

- 阅读[配置文档](settings.md)了解更多配置选项
- 查看[使用说明](usage.md)了解如何配置定时任务
- 参考[开发指南](develop.md)了解如何扩展功能
- 查看[故障排除](troubleshooting.md)解决常见问题

## 接口支持情况

**说明：** 本项目目前已支持 Tushare 的全量 API（不包括已停止更新的接口）。请注意，Tushare 官网文档中部分接口并非以 API 形式提供，例如"复权行情"以及期货 Tick 行情等。若您发现有遗漏或错误，欢迎提交 Issue 至项目仓库。

## 目前支持的数据库

- [Clickhouse](https://clickhouse.com)
- [Apache Doris](https://doris.apache.org/)(未测试)
- [MySQL](https://www.mysql.com/)(未完全测试)
- [StarRocks](https://www.starrocks.io/)(使用PrimaryKey模型)
- 其他数据库欢迎提交PR

## 使用建议

- Tushare账号积分大于等于5000分以获得最佳体验，需要采集筹码分布数据建议15000积分以上
- 使用Docker镜像运行项目以避免依赖问题

## 平台/工具

- [Tushare Pro](https://tushare.pro/) 金融数据接口平台
- [httpx](https://www.python-httpx.org/) HTTP 请求客户端库
- [Docker](https://www.docker.com/) 容器化运行环境
- [Pydantic](https://docs.pydantic.dev/latest/) 用于参数校验
- [Typer](https://typer.tiangolo.com/) 命令行参数解析
- [Rich](https://rich.readthedocs.io/en/stable/introduction.html) 命令行输出美化
- [PyYAML](https://pyyaml.org/) 配置文件解析
- [Pandas](https://pandas.pydata.org/) 数据处理库
- [SQLAlchemy](https://www.sqlalchemy.org/) 数据库访问库
- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) 文档生成工具
