# 开发指南

### 所需知识

基于Tushare HTTP API进行数据集成，开发时需了解：

为了顺利开发和扩展本项目，建议具备以下相关知识和技能：

1. **Tushare Pro 接口及数据服务**  
   - 熟悉 Tushare Pro 提供的 HTTP API 及接口文档，包括申请 token、查询请求参数和解析返回数据。  
   - 理解 Tushare 积分机制以及不同数据接口调用的频次限制。

2. **Python 编程**  
   - 掌握 Python 基本语法和面向对象编程思想，了解异步编程和 HTTP 请求库（如 httpx）的使用方法。

3. **SQLAlchemy 与 ORM**  
   - 熟悉 SQLAlchemy 的基本用法和 ORM（对象关系映射）原理，能够基于 SQLAlchemy 定义数据模型。  
   - 理解如何在模型中配置 `__table_args__` 来支持不同数据库引擎（如 ClickHouse、MySQL、Apache Doris、StarRocks）。

4. **数据库知识**  
   - 熟悉常见关系型数据库（如 MySQL）以及分布式数据库（如 ClickHouse）的基本原理和操作。  
   - 了解常用数据库引擎特点，如 InnoDB、ReplacingMergeTree 及 PrimaryKey 模型，并明白其在数据存储中的作用。

5. **爬虫开发与数据集成**  
   - 理解爬虫系统的基本架构和工作流程，本项目所有爬虫均继承自 `Spider`，并通过 `SpiderMeta` 自动注册，实现统一管理与调度。  
   - 熟悉爬虫实现流程，包括请求生成、响应解析以及数据处理 Pipeline（如 FillNAPipeline、TransformDTypePipeline、DataPipeline、RecordLogPipeline）的使用与扩展。

6. **配置管理与日志系统**  
   - 掌握使用 YAML 文件和环境变量进行配置管理，了解 Pydantic BaseSettings 的使用方法。  
   - 理解日志系统的工作原理，能够利用日志模块对爬虫运行过程进行调试和监控.

7. **容器化及部署**  
   - 掌握 Docker 镜像构建与部署技术，了解 Kubernetes（Helm）部署和 CronJob 定时任务的配置方法。  
   - 熟悉使用命令行工具（如 typer）管理爬虫任务和查看 API 信息的基本操作.

### BaseSpiders

**所有爬虫均继承自 Spider，并通过 SpiderMeta 自动注册**

开发者在实现新的爬虫时，可以选择以下基类以复用通用功能：
- **TushareSpider**：用于所有 Spider 的基础实现，内置了自动建表逻辑和 HTTP Request 生成功能；大多数爬虫均可基于 TushareSpider 进行扩展。
- **TimeSeriesSpider**：专为按日采集数据设计。该爬虫支持基于交易日历的补数策略，当目标表缺少某个交易日数据时，会自动发起采集请求，其采集起始日期由模型中的 `__start_date__` 属性决定。
- **TSCodeSpider**：适用于基于 ts_code 采集数据的场景。此基类要求开发者通过设置 `__basic_table__` 属性来指定基础表，从该表中读取 ts_code 字段，并针对每个 ts_code 发起数据采集请求。
- **FinancialReportSpider**：用于采集财务报表数据，会根据 Tushare 积分情况自动判断是否采用 VIP 接口进行数据采集。
- **LimitOffsetSpider**：用于处理数据分页请求场景，利用 limit 和 offset 参数实现逐页数据请求，适用于数据量较大的接口。

开发者可使用项目提供的命令行工具来列出和管理所有已注册的爬虫，从而实现灵活调度和扩展。

### Pipelines

- **FillNAPipeline**：遍历目标数据模型的所有字段，根据字段类型自动填充缺失值。  
  - 如果字段设置了默认值，则使用该默认值，否则根据字段类型返回空字符串（str）、0 或 0.0（数值）、"1970-01-01"（日期）、"1970-01-01 00:00:00"（日期时间）等。  
  - 该管道确保数据在进一步转换或入库前不会因缺失值影响后续操作。

- **TransformDTypePipeline**：基于数据模型字段的类型定义，对传入的 DataFrame 数据进行数据类型转换。  
  - 分别将数据转换为字符串、浮点数、整数类型，并对日期、日期时间字段进行标准化处理（例如使用 `pd.to_datetime` 进行解析）。
  - 该管道保证数据类型与数据库表结构一致，避免因数据格式问题导致插入失败。

- **DataPipeline**：实现数据存储功能。  
  - 在处理数据前，会通过 DBEngine 自动创建目标数据库表（依据 SQLAlchemy 模型中定义的 __table_args__）。  
  - 如果数据模型定义了主键，会对数据进行去重并采用 upsert（更新或插入）的策略；否则直接进行插入操作。  
  - 该管道封装了对数据库的写入细节，支持多种数据库（如 ClickHouse、MySQL、Apache Doris、StarRocks）。

- **RecordLogPipeline**：记录数据集成处理过程中的日志信息。  
  - 在数据传递过程中累计处理的数据条数，并在管道关闭时将批次 ID、爬虫名称、API 描述、数据计数、开始与结束时间记录到日志表中。  
  - 该日志记录有助于后续故障排查和监控数据同步情况。

### 数据库支持

项目基于SQLAlchemy实现，通过灵活的ORM映射和数据库引擎配置提供了多种数据库的支持，目前已集成以下数据库：

- **ClickHouse**：利用 clickhouse_sqlalchemy 提供的 ReplacingMergeTree 引擎，实现高效数据写入与查询。
- **Apache Doris**：支持通过自定义引擎选项与 Doris 前端进行数据交互（未完全测试）。
- **MySQL**：借助 InnoDB 引擎实现数据存储，保证兼容性与稳定性。
- **StarRocks**：采用 PrimaryKey 模型，实现分布式数据存储与快速查询。

每个数据库的配置均在对应数据模型的 __table_args__ 中详细设置，以匹配各自数据库的特性。如果需要扩展支持其他数据库，只需按照以下步骤操作：

1. 添加或引入该数据库对应的 SQLAlchemy 方言或驱动；
2. 在数据模型中配置或修改 __table_args__，设置相应的引擎和选项；
3. 更新数据库引擎类（DBEngine）中 create_table、insert、upsert 等操作的实现，确保适配新的数据库。

这种设计使得项目能够灵活适配多种数据库，同时方便用户根据业务场景自定义扩展其他数据库支持。

所有继承自 `Spider` 的爬虫会自动注册到 `SpiderMeta`，实现对所有爬虫的统一管理、调度与 API 信息查询。用户可以通过命令行工具列出当前可用爬虫及其详细信息，从而方便扩展和调试。