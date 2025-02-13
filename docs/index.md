# 项目介绍

## 项目背景

Tushare Pro 是一个广受欢迎的金融数据服务平台，为数据分析人员、量化交易者和研究人员提供了全面的金融市场数据。然而，在实际应用中，API 调用频次限制可能会影响数据分析的效率和深度。

为了解决这个问题，我们开发了 Tushare Integration，它提供以下核心功能：
1. 自动化数据同步：将 Tushare Pro 的数据定期同步到本地数据库
2. 智能增量更新：通过增量更新机制，最小化数据同步开销
3. 多数据库支持：兼容多种主流数据库系统

## 项目目标

- 提供稳定可靠的数据同步方案，确保数据的及时性和准确性
- 支持灵活的数据同步策略，包括全量同步与增量更新
- 实现多种主流数据库的无缝对接
- 提供简单易用的命令行工具，降低使用门槛
- 保持与 Tushare Pro 接口的同步更新
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
  drivername: "clickhouse+http" # 必填，可通过环境变量 DB_DRIVER 设置
  host: "127.0.0.1" # 必填，可通过环境变量 DB_HOST 设置
  port: 8123 # 必填，可通过环境变量 DB_PORT 设置
  user: "default" # 必填，可通过环境变量 DB_USER 设置
  password: "" # 可选，可通过环境变量 DB_PASSWORD 设置
  db_name: "default" # 必填，可通过环境变量 DB_NAME 设置
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

**说明：** 本项目已实现对 Tushare Pro 全量 API 的支持（不含已停止更新的接口）。需要注意的是，Tushare 官方文档中的部分数据（如"复权行情"、期货 Tick 行情等）并非以 API 形式提供，因此不在支持范围内。

**重要提示：** 由于 Tushare Pro 接口数量庞大且持续更新，我们无法对所有接口进行全面测试。强烈建议用户在首次数据集成后，务必验证数据的完整性和准确性。如遇到任何问题，欢迎通过 Issue 向我们反馈。

## 目前支持的数据库

- [StarRocks](https://www.starrocks.io/) - 使用 PrimaryKey 模型，适合实时分析场景
- [ClickHouse](https://clickhouse.com/) - 高性能列式数据库
- [MySQL](https://www.mysql.com/)
- [Apache Doris](https://doris.apache.org/) 
- 欢迎贡献更多数据库支持

## 使用建议

- 账号要求：建议使用 5000 积分以上的 Tushare Pro 账号以获得最佳体验
- 特殊数据：采集筹码分布等高级数据需要 15000 积分以上的账号
- 部署方式：
  - Docker部署：推荐使用官方提供的 Docker 镜像，可避免环境依赖问题
  - pip安装：支持通过 pip 安装，建议使用虚拟环境以避免依赖冲突
- 数据验证：首次使用请进行数据完整性验证
- 配置优化：根据实际需求调整同步频率和并发设置

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
