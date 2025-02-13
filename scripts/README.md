# 脚本工具

本目录包含项目使用的工具脚本：

## Python 脚本

- `batch_run.sh` - 批量触发所有 Kubernetes cronjob 的 Bash 脚本
- `create_table.py` - 生成模型的 SQL DDL 语句并打印示例查询
- `generate_jobs.py` - 生成数据爬虫的 Kubernetes cronjob 配置
- `generate_models.py` - 从 Tushare API 文档生成 SQLAlchemy 模型类
- `generate_models_init.py` - 生成 models 包的 __init__.py 文件
- `get_categories.py` - 从 Tushare 文档提取 API 分类信息
- `migrate_metadata.py` - 将依赖和主键元数据从 schema 文件迁移到模型类
- `migrate_start_date.py` - 根据硬编码配置更新模型类中的起始日期
- `publish.py` - 处理包的构建和发布到 PyPI

主要功能：

- 模型生成和元数据管理
- Schema 和依赖迁移
- 包发布工具
- 数据库表创建助手
- 任务配置生成
- 分类信息提取

所有脚本都有适当的错误处理和日志记录。许多脚本需要配置（如 Tushare API 令牌或数据库凭据）才能运行。  

详细文档和使用说明请参见各个脚本文件。
