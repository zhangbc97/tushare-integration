# 配置文件

与标准的scrapy项目不同，项目的配置文件不是 `settings.py`，而是 `config.yaml`，并提供了基于环境变量的配置方式。

### 注意事项

- 环境变量的优先级高于配置文件
- 部分配置项未在文档中列举，意味着不建议修改

### jobs.yaml

项目支持使用jobs.yaml配置文件来简化采集配置，一个job中可以包含多个spider，可以通过定制jobs.yaml文件来按批次采集数据。  
**项目本身并不支持使用Cron表达式自动进行定时采集，需要用户自行配置定时任务，使用K8S的用户将会自动创建CronJob**

配置文件示例如下

```yaml
cronjob:
  - name: daily_morning  #Job名称
    cron_expr: '0 8 * * 1-5'   # 非K8S部署下该参数不生效
    spiders:
      - name: "stock/basic/stock_basic"  # Spider名称
      - name: "stock/basic/stock_company"
  - name: daily_open
    cron_expr: '40 9 * * 1-5'
    spiders:
      - name: "stock/quotes/adj_factor"
      - name: "stock/special/.*"    # 支持使用正则表达式匹配（全文匹配）
```

### config.yaml

#### Tushare相关

| 配置项                            | 环境变量        | 类型  | 默认值                  | 说明                                                   |
| --------------------------------- | --------------- | ----- | ----------------------- | ------------------------------------------------------ |
| `tushare_token`                   | `TUSHARE_TOKEN` | `str` | 无默认值 (必填)         | Tushare账号 Token                                      |
| `tushare_url`                     |                 | `str` | https://api.tushare.pro | Tushare服务地址                                        |
| `tushare_point`                   |                 | `int` | 2000                    | Tushare服务积分                                        |
| `tushare_max_concurrent_requests` |                 | `int` | 基于积分计算            | 自动计算每分钟最大并发请求数；若手动指定则跳过自动计算 |

#### 任务及调度配置

| 配置项               | 环境变量             | 类型   | 默认值        | 说明                                         |
| -------------------- | -------------------- | ------ | ------------- | -------------------------------------------- |
| `batch_id`           | `BATCH_ID`           | `str`  | 自动生成 UUID | 批次ID，用于数据库写入和通知；不填则自动生成 |
| `parallel_mode`      |                      | `bool` | False         | 并行模式，开启后将关闭自动依赖解析           |
| `concurrent_spiders` | `CONCURRENT_SPIDERS` | `int`  | 1             | 并发爬虫数，用于控制同时运行的爬虫数量       |

#### 数据库相关

数据库配置存放于 `database` 下，支持的数据库包括 `clickhouse`、`doris`、`mysql` 等。

| 配置项            | 环境变量      | 类型   | 默认值   | 说明                                                   |
| ----------------- | ------------- | ------ | -------- | ------------------------------------------------------ |
| `drivername`      | `DB_DRIVER`   | `str`  | 无默认值 | 数据库驱动名称，例如：clickhouse+native, mysql+pymysql |
| `host`            | `DB_HOST`     | `str`  |          | 数据库地址                                             |
| `port`            | `DB_PORT`     | `int`  |          | 数据库端口                                             |
| `user`            | `DB_USER`     | `str`  |          | 数据库用户名                                           |
| `password`        | `DB_PASSWORD` | `str`  | ""       | 数据库密码                                             |
| `db_name`         | `DB_NAME`     | `str`  |          | 数据库名称                                             |
| `template_params` |               | `dict` | {}       | SQL模板参数                                            |

#### Reporters相关配置

| 配置项           | 环境变量         | 类型        | 默认值 | 说明              |
| ---------------- | ---------------- | ----------- | ------ | ----------------- |
| `reporters`      |                  | `list[str]` | []     | Reporter 清单     |
| `feishu_webhook` | `FEISHU_WEBHOOK` | `str`       | ""     | 飞书 Webhook 地址 |

#### 爬虫及请求配置

| 配置项                    | 环境变量    | 类型                                        | 默认值                                | 说明                   |
| ------------------------- | ----------- | ------------------------------------------- | ------------------------------------- | ---------------------- |
| `download_delay`          |             | `float`                                     | 0                                     | 下载延迟（秒）         |
| `max_requests_per_minute` |             | `int`                                       | 60                                    | 每分钟最大请求数       |
| `retry_enabled`           |             | `bool`                                      | True                                  | 是否启用请求重试       |
| `retry_times`             |             | `int`                                       | 10                                    | 重试次数               |
| `retry_delay`             |             | `int`                                       | 10                                    | 请求失败重试间隔（秒） |
| `timeout`                 |             | `int`                                       | 30                                    | 请求超时时间（秒）     |
| `headers`                 |             | `dict[str, str]`                            | {"User-Agent": "tushare-integration"} | 请求头                 |
| `log_level`               | `LOG_LEVEL` | `Literal['DEBUG','INFO','WARNING','ERROR']` | 'INFO'                                | 日志级别               |

