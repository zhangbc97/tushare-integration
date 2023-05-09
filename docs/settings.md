# 配置文件

与标准的scrapy项目不同，项目的配置文件不是 `settings.py`，而是 `config.yaml`，并提供了基于环境变量的配置方式。

### 注意事项

- 环境变量的优先级高于配置文件
- 部分配置项未在文档中列举，意味着不建议修改

### 可用的配置项

#### Tushare相关

| 配置项                               | 环境变量            | 类型    | 默认值                     | 说明                            |
|-----------------------------------|-----------------|-------|-------------------------|-------------------------------|
| `tushare_url`                     | `TUSHARE_URL`   | `str` | https://api.tushare.pro | Tushare服务地址                   |
| `tushare_point`                   | `TUSHARE_POINT` | `int` | 2000                    | Tushare服务积分                   |
| `tushare_token`                   | `TUSHARE_TOKEN` | `str` | ""                      | Tushare账号Token                |
| `tushare_max_concurrent_requests` | ``              | `int` | 基于积分计算                  | 基于积分自动计算最大每分钟并行请求数，如果指定则会跳过计算 |

#### 数据库相关

| 配置项            | 环境变量           | 类型    | 默认值 | 说明                             |
|----------------|----------------|-------|-----|--------------------------------|
| `db_uri`       | `DB_URI`       | `str` | ""  | SQLAlchemy连接串                  |
| `db_name`      | `DB_NAME`      | `str` | ""  | 数据库名称                          |
| `sql_template` | `SQL_TEMPLATE` | `str` | ""  | SQL模板，目前可选值 `mysql`,`databend` |

#### Reporters

reporters可选值

- ` tushare_integration.reporters.FeishuWebHookReporter` 飞书WebHook

| 配置项              | 环境变量             | 类型          | 默认值 | 说明          |
|------------------|------------------|-------------|-----|-------------|
| `reporters`      |                  | `list[str]` | []  | Reporter清单  |
| `feishu_webhook` | `FEISHU_WEBHOOK` | `str`       | ""  | 飞书WebHook地址 |

#### Scrapy配置

| 配置项                   | 环境变量 | 类型     | 默认值                   | 说明              |
|-----------------------|------|--------|-----------------------|-----------------|
| `bot_name`            |      | `str`  | "tushare_integration" | Scrapy Bot Name |
| `concurrent_requests` |      | `int`  | 10                    | 最大并发请求          |
| `concurrent_items`    |      | `int`  | 100                   | Pipeline最大并行处理数 |
| `retry_enabled`       |      | `bool` | true                  | 是否开启请求失败重试      |
| `retry_delay`         |      | `int`  | 10                    | 重试延迟时间(秒)       |
| `retry_times`         |      | `int`  | 6                     | 最大重试次数          |

