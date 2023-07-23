# 项目介绍

## 项目背景

Tushare Pro目前已稳定运行几年时间，其提供了大量的金融数据接口，不过Tushare Pro接口在使用过程中有频次限制，在数据分析过程中，我们希望能够不受限制的访问数据库，
因此需要在每日更新后，将数据同步到本地数据库中。Tushare Integration就是为了解决这个问题而生。

## 项目目标

- 实现同步 Tushare Pro 接口数据到本地数据库，并支持全量同步与增量更新
- 支持将数据写入到多种数据库

## 目前支持的接口

- 沪深股票
    - 基础数据
    - 行情数据(不包含通用行情)
    - 财务数据
    - 市场参考数据（部分）
    - 特色数据（部分）
- 指数
    - 指数基本信息
- 期货
    - 期货合约信息
    - 期货交易日历
    - 期货日线行情
    - 每日持仓排名
    - 仓单日报
    - 每日结算参数

## 目前支持的数据库

- [Clickhouse](https://clickhouse.com)
- [Databend](https://databend.rs/)
- [MySQL](https://www.mysql.com/)(未完全测试)
- 其他数据库欢迎提交PR

## 使用建议

- Tushare账号积分大于等于5000分以获得最佳体验
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
