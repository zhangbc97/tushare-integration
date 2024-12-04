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

## 目前支持的接口

下列列表来自于Tushare Pro官方文档，标注了已完成的接口和不计划支持的接口

- 沪深股票
    - [x] 基础数据
        - [x] 股票列表
        - [x] 股本情况（盘前）
        - [x] 交易日历
        - [x] 股票曾用名
        - [x] 沪深股通成分股
        - [x] 上市公司基本信息
        - [x] 上市公司管理层
        - [x] 管理层薪酬和持股
        - [x] IPO新股上市
        - [x] 备用列表
    - [x] 行情数据
        - [x] 日线行情
        - [x] 周线行情
        - [x] 月线行情
        - [x] 股票周/月线行情(每日更新)
        - [ ] ~~复权行情~~(非API)
        - [x] 复权因子
        - [ ] ~~停复牌信息(停)~~(官方已停止支持)
        - [x] 每日停复牌信息
        - [x] 每日指标
        - [ ] ~~通用行情接口~~(非API)
        - [x] 每日涨跌停价格
        - [x] 沪深股通十大成交股
        - [x] 港股通十大成交股
        - [x] 港股通每日成交统计
        - [ ] ~~港股通每月成交统计~~(官方数据未持续更新)
        - [x] 备用行情
        - [x] 1分钟行情
    - [x] 打板专题数据
        - [x] 同花顺涨跌停榜单
        - [x] 涨跌停列表（新版）
        - [x] 涨停股票连板天梯
        - [x] 涨停最强板块统计
        - [x] 榜单数据（开盘啦）
        - [x] 题材数据（开盘啦）
        - [x] 题材成分（开盘啦）
        - [x] 同花顺热榜
        - [x] 东财热榜
        - [x] 游资名录
        - [x] 游资每日明细
        - [x] 涨跌停和炸板数据
    - [x] 财务数据
        - [x] 利润表
        - [x] 资产负债表
        - [x] 现金流量表
        - [x] 业绩预告
        - [x] 业绩快报
        - [x] 分红送股数据
        - [x] 财务指标数据
        - [x] 财务审计意见
        - [x] 主营业务构成
        - [x] 财报披露日期表
    - [x] 市场参考数据
        - [x] 融资融券标的(盘前)
        - [x] 前十大股东
        - [x] 前十大流通股东
        - [x] 龙虎榜每日交易
        - [x] 龙虎榜机构交易明细
        - [x] 股权质押统计数据
        - [x] 股权质押明细数据
        - [x] 股票回购
        - [x] 概念股分类表
        - [x] 概念股明细列表
        - [x] 限售股解禁
        - [x] 大宗交易
        - [ ] ~~股票开户数据(停)~~
        - [ ] ~~股票开户数据(旧)~~
        - [x] 股东人数
        - [x] 股东增减持
    - [x] 特色数据
        - [x] 券商盈利预测数据
        - [x] 每日筹码及胜率
        - [x] 每日筹码分布
        - [x] 股票技术面因子
        - [x] 股票技术面因子(专业版)
        - [x] 中央结算系统持股统计
        - [x] 中央结算系统持股明细
        - [x] 沪深股通持股明细
        - [x] 结构调研数据
        - [x] 券商月度金股
    - [x] 两融及转融通
        - [x] 融资融券交易汇总
        - [x] 融资融券交易明细
        - [x] 转融资交易汇总
        - [x] 转融券交易汇总
        - [x] 转融券交易明细
        - [x] 做市借券交易汇总
    - [x] 资金流向数据
        - [x] 每日涨跌停价格
        - [x] 沪深港通资金流向
        - [x] 个股资金流向(THS)
        - [x] 个股资金流向(DC)
        - [x] 行业资金流向(THS)
        - [x] 板块资金流向(DC)
        - [x] 大盘资金流向(DC)
- [x] 指数
    - [x] 指数基本信息
    - [x] 指数日线行情
    - [x] 指数周线行情
    - [x] 指数月线行情
    - [x] 指数成份和权重
    - [x] 大盘指数每日指标
    - [x] 申万行业分类
    - [x] 申万行业成份
    - [x] 申万行业成分（分级）
    - [x] 沪深市场每日交易统计
    - [x] 深圳市场每日交易情况
    - [x] 同花顺概念和行业列表
    - [x] 同花顺概念和行业指数行情
    - [x] 同花顺概念和行业指数成分
    - [x] 中信行业指数日行情
    - [x] 申万行业指数日行情
    - [x] 国际主要指数
- [x] 期货
    - [x] 期货合约信息
    - [x] 期货交易日历(股票交易日历采集会自动包含期货交易日历)
    - [x] 期货日线行情
    - [x] 每日持仓排名
    - [x] 仓单日报
    - [x] 每日结算参数
    - [x] 南华期货指数日线行情(与指数日线行情同一接口)
    - [x] 期货主力与连续合约
    - [x] 期货主要品种交易周报
    - [ ] ~~期货Tick行情(非API)~~

## 目前支持的数据库

- [Clickhouse](https://clickhouse.com)
- [Apache Doris](https://doris.apache.org/)(未测试)
- [MySQL](https://www.mysql.com/)(未完全测试)
- 其他数据库欢迎提交PR

## 使用建议

- Tushare账号积分大于等于5000分以获得最佳体验，需要采集筹码分布数据建议15000积分以上
- 使用Docker镜像运行项目以避免依赖问题

## 平台/工具

- [Tushare Pro](https://tushare.pro/) 金融数据接口平台
- [Scrapy](https://scrapy.org/) 数据采集框架
- [Docker](https://www.docker.com/) 容器化运行环境
- [Pydantic](https://docs.pydantic.dev/latest/) 用于参数校验
- [Typer](https://typer.tiangolo.com/) 命令行参数解析
- [Rich](https://rich.readthedocs.io/en/stable/introduction.html) 命令行输出美化
- [PyYAML](https://pyyaml.org/) 配置文件解析
- [Jinja2](https://jinja.palletsprojects.com/en/3.0.x/) 模板引擎
- [Pandas](https://pandas.pydata.org/) 数据处理库
- [SQLAlchemy](https://www.sqlalchemy.org/) 数据库访问库
- [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) 文档生成工具
