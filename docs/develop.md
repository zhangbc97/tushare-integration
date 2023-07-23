# 开发指南

### 所需知识

- 项目开发时以scrapy为基础，因此需要了解scrapy的基本使用方法

### BaseSpiders

**所有的Spider均是TushareSpider的子类**

| BaseSpider            | 功能              | 备注                                                                                                                       |
|-----------------------|-----------------|--------------------------------------------------------------------------------------------------------------------------|
| TushareSpider         | 用于所有Spider的基类   | TushareSpider为所有Spider的基类，内部包含自动建表的逻辑以及HTTP Request生成逻辑                                                                  |
| DailySpider           | 用于按日采集数据        | <li>DailySpider用于按日采集数据，将会按照交易日历寻找开盘日期，如果日期不存在目标表中，则会采集对应日期的数据 </li> <li>可通过`{{ custom_settings.MIN_CAL_DATE}}`减小范围</li> |
| TSCodeSpider          | 用于根据ts_code采集数据 | TSCodeSpider将会读取`{{ custom_settings.BASIC_TABLE }}`中的ts_code清单，然后根据ts_code进行数据采集                                         |
| FinancialReportSpider | 用于采集财务报表数据      | 当大于5000积分时，可使用vip接口进行数据采集，FinancialReportSpider将会根据积分判断使用不同的接口                                                           |

### Pipelines

- TushareIntegrationFillNAPipeline 用于使用默认值填充缺失值
- TransformDTypePipeline 用于转换数据类型
- TushareIntegrationDataPipeline 用于将数据写入数据库
- RecordLogPipeline 用于记录日志

### 数据库支持

项目使用模板引擎生成SQL语句，只需要配置好对应数据库的模板，即可支持对应的数据库。  
新增一个数据库需要提供三个模板文件，放置于 `tushare_integration/schema/template/{database}` 目录下

- `insert.jinja2` 用于生成插入语句
- `create.jinja2` 用于生成建表语句，当Spider启动时会自动使用table.jinja2建表，建表语句请使用`CREATE TABLE IF NOT EXIST`
  ，当表结构发生变化时，需要手动修改表结构
- `upsert.jinja2` 用于生成更新或插入语句,数据库需要支持UPSERT能力，例如`REPLACE INTO`

