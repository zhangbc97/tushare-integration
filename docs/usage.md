# 使用方式

- 参考[配置文件](settings.md)编写好配置文件
- 使用python main.py启动主程序

## 命令列表

- **run**: 运行爬虫或任务，在项目运行时调用不同的爬虫和任务。
  - **run spider**: 运行指定爬虫，支持通配符匹配  
    例如：`python main.py run spider stock/basic/stock_basic` 运行单个爬虫，或 `python main.py run spider stock/basic/*` 运行该目录下全部爬虫。可使用 `--verbose` 参数增加调试日志输出。
  - **run job**: 运行预定义任务，通过jobs.yaml进行任务调度  
    例如：`python main.py run job daily_morning` 运行名为 daily_morning 的任务，此命令会自动读取默认配置文件（config.yaml）。

- **spider**: 爬虫管理命令，用于查看所有爬虫列表及详细信息。
  - **spider list**: 列出所有可用爬虫，展示爬虫名称、对应 API 接口及数据路径  
    例如：`python main.py spider list`
  - **spider info**: 查看指定爬虫的详细信息，包括数据处理逻辑与依赖关系  
    例如：`python main.py spider info stock/basic/stock_basic`

- **api**: API管理命令，用于查询 API 文档和接口使用情况。
  - **api list**: 列出所有可用 API，展示接口名称、所需积分、特殊权限以及参数信息  
    例如：`python main.py api list`
  - **api info**: 查看指定 API 的详细信息，包括分类、详细参数说明和依赖关系  
    例如：`python main.py api info stock_basic`

- **config**: 配置管理命令，帮助用户交互式生成和修改配置文件。
  - **config init**: 交互式初始化配置，生成默认的 config.yaml 及（可选的）jobs.yaml 文件  
    例如：`python main.py config init`

## 使用示例

### 1. 运行单个爬虫
```bash
# 运行股票基本信息爬虫
python main.py run spider stock/basic/stock_basic
```

### 2. 运行一组爬虫
```bash
# 运行所有基本信息相关的爬虫
python main.py run spider stock/basic/*
```

### 3. 运行预定义任务
```bash
# 运行daily_morning任务
python main.py run job daily_morning
```

### 4. 查看爬虫信息
```bash
# 列出所有可用爬虫
python main.py spider list

# 查看特定爬虫的详细信息
python main.py spider info stock/basic/stock_basic
```

### 5. 查看API信息
```bash
# 查看股票基本信息API的详细信息
python main.py api info stock_basic
```

## 使用K8S

项目提供了基于Helm的部署模板，编写好values.yaml后直接部署到集群即可，会自动创建CronJob用于定时更新

## 使用Docker

### 安装Docker

```shell
yum install -y yum-utils
yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
yum install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl start docker
```

### 部署Clickhouse

#### 拉取镜像

```shell
docker pull clickhouse/clickhouse-server:23.6.2.18-alpine
```

#### 创建数据目录

```shell
mkdir -p /data0/clickhouse/data
```

#### 创建配置文件目录（可选）

```shell
mkdir -p /data0/clickhouse/config
```

#### 启动数据库

如果不需要挂载配置文件删除下列命令中的`-v /data0/clickhouse/config:/etc/clickhouse-server/config.d`

```shell
docker run -d --net=host -v /data0/clickhouse/data:/var/lib/clickhouse -v /data0/clickhouse/config:/etc/clickhouse-server/config.d --name clickhouse-server --ulimit nofile=262144:262144 clickhouse/clickhouse-server:23.6.2.18-alpine
```

### tushare-integration

#### 创建配置文件目录

```shell
mkdir -p /data0/tushare-integration/config
```

#### 编写jobs.yaml和config.yaml

```yaml
# jobs.yaml
cronjob:
  - cron_expr: Unsupported
    name: stock/basic
    spiders:
      - name: stock/basic/stock_basic
      - name: stock/basic/namechange
      - name: stock/basic/hs_const
      - name: stock/basic/trade_cal
      - name: stock/basic/stock_company
      - name: stock/basic/stk_managers
      - name: stock/basic/stk_rewards
      - name: stock/basic/new_share
      - name: stock/basic/bak_basic
  - cron_expr: Unsupported
    name: stock/financial
    spiders:
      - name: stock/financial/balancesheet
      - name: stock/financial/cashflow
      - name: stock/financial/income
      - name: stock/financial/express
      - name: stock/financial/forecast
      - name: stock/financial/dividend
      - name: stock/financial/fina_indicator
      - name: stock/financial/fina_audit
      - name: stock/financial/fina_mainbz
      - name: stock/financial/disclosure_date
  - cron_expr: Unsupported
    name: stock/market
    spiders:
      - name: stock/market/margin
      - name: stock/market/margin_detail
      - name: stock/market/margin_target
      - name: stock/market/top10_holders
      - name: stock/market/top10_floatholders
      - name: stock/market/top_list
      - name: stock/market/top_inst
      - name: stock/market/pledge_stat
      - name: stock/market/pledge_detail
      - name: stock/market/repurchase
      - name: stock/market/concept
      - name: stock/market/concept_detail
      - name: stock/market/block_trade
      - name: stock/market/stk_holdernumber
      - name: stock/market/stk_holdertrade
  - cron_expr: Unsupported
    name: stock/quotes
    spiders:
      - name: stock/quotes/daily
      - name: stock/quotes/weekly
      - name: stock/quotes/monthly
      - name: stock/quotes/adj_factor
      - name: stock/quotes/suspend_d
      - name: stock/quotes/hsgt_top10
      - name: stock/quotes/moneyflow
      - name: stock/quotes/moneyflow_hsgt
      - name: stock/quotes/stk_limit
      - name: stock/quotes/daily_basic
      - name: stock/quotes/ggt_top10
      - name: stock/quotes/ggt_daily
      - name: stock/quotes/bak_daily
  - cron_expr: Unsupported
    name: stock/special
    spiders:
      - name: stock/special/report_rc
      - name: stock/special/cyq_perf
      - name: stock/special/stk_factor
      - name: stock/special/ccass_hold
      - name: stock/special/ccass_hold_detail
      - name: stock/special/hk_hold
      - name: stock/special/limit_list_d
      - name: stock/special/stk_surv
      - name: stock/special/broker_recommend

```

```yaml
# config.yaml
# TUSHARE相关配置
tushare_url: https://api.tushare.pro
tushare_point: 2000
tushare_token: ''

database:
  # 数据库配置
  db_type: 'clickhouse'
  host: '127.0.0.1'
  port: '8123'
  user: 'default'
  password: ''
  db_name: 'default'
  template_params: { }

reporters: [ ]
#  - "tushare_integration.reporters.FeishuWebHookReporter"

# 飞书Webhook配置
feishu_webhook: ""

# Scrapy配置
bot_name: tushare_integration
concurrent_requests: 1
concurrent_items: 100

downloader_middlewares:
  scrapy.downloadermiddlewares.retry.RetryMiddleware: null
  tushare_integration.middlewares.TushareRetryDownloaderMiddleware: 543

item_pipelines:
  tushare_integration.pipelines.TushareIntegrationFillNAPipeline: 298
  tushare_integration.pipelines.TransformDTypePipeline: 299
  tushare_integration.pipelines.TushareIntegrationDataPipeline: 300
  tushare_integration.pipelines.RecordLogPipeline: 301


# 重试配置
# Tushare的频次限制是一分钟为周期，重试只要大于这个周期理论上不会有任何问题
retry_enabled: true
retry_delay: 10
retry_times: 6

spider_modules:
  - "tushare_integration.spiders"

closespider_errorcount: 1
```

#### 手动运行任务

```shell
docker run -d --net=host -v /data0/tushare-integration/config/jobs.yaml:/code/app/jobs.yaml -v /data0/tushare-integration/config/config.yaml:/code/app/config.yaml zhangbc/tushare-integration:0.0.3 python main.py run job stock/basic 
```

#### 配置定时任务

配置定时任务时请避免定时任务同时启动，采集服务并发情况下可能会出现采集的数据异常

```shell
crontab -e
```

### 使用Crontab定时运行Job

将jobs.yaml和config.yaml文件放置在同一目录下，然后在crontab中添加上述命令
