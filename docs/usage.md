# 使用方式

- 参考配置文件模块编写好配置文件或设置好环境变量
- 使用python main.py启动主程序

## 命令

### query

#### list 列举spider清单

`python main.py query list [OPTIONS]`

### run

#### spider 运行爬虫

`python main.py run spider [OPTIONS] SPIDER_NAME`

该命令将运行对应的spider  
spider_name基于正则匹配，例如stock/basic/*将运行所有stock/basic下的spider

#### job 运行任务

`python main.py run job [OPTIONS] JOB_NAME`

该命令将从jobs.yaml文件中找到对应的job，然后运行该job下的所有spider