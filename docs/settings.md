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

| 配置项                               | 环境变量            | 类型    | 默认值                     | 说明                            |
|-----------------------------------|-----------------|-------|-------------------------|-------------------------------|
| `tushare_url`                     | `TUSHARE_URL`   | `str` | https://api.tushare.pro | Tushare服务地址                   |
| `tushare_point`                   | `TUSHARE_POINT` | `int` | 2000                    | Tushare服务积分                   |
| `tushare_token`                   | `TUSHARE_TOKEN` | `str` | ""                      | Tushare账号Token                |
| `tushare_max_concurrent_requests` | ``              | `int` | 基于积分计算                  | 基于积分自动计算最大每分钟并行请求数，如果指定则会跳过计算 |

#### 数据库相关

数据库相关配置在 `databases` 下，目前支持的数据库有 `clickhouse`、`databend`、`mysql`，每个数据库的配置项不同，具体请参考下表。

| 配置项               | 环境变量          | 类型     | 默认值 | 说明     |
|-------------------|---------------|--------|-----|--------|
| `db_type`         | `DB_TYPE`     | `str`  |     | 数据库类型  |
| `host`            | `DB_HOST`     | `str`  |     | 数据库地址  |
| `port`            | `DB_PORT`     | `int`  |     | 数据库端口  |
| `user`            | `DB_USER`     | `str`  |     | 数据库用户名 |
| `password`        | `DB_PASSWORD` | `str`  |     | 数据库密码  |
| `db_name`         | `DB_NAME`     | `str`  |     | 数据库名称  |
| `template_params` | ``            | `dict` | {}  | 模板参数   |

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

