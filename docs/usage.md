# 使用方式

- 参考[配置文件](settings.md)编写好配置文件
- 使用python main.py启动主程序

## 命令

### query

#### list 列举spider清单

`python main.py query list [OPTIONS]`

### run

#### spider 运行爬虫

`python main.py run spider [OPTIONS] SPIDER_NAME`

该命令将运行对应的spider  
spider_name基于正则全文匹配，例如stock/basic/*将运行所有stock/basic下的spider

#### job 运行任务

`python main.py run job [OPTIONS] JOB_NAME`

该命令将从jobs.yaml文件中找到对应的job，然后运行该job下的所有spider

## 使用K8S

项目提供了基于Helm的部署模板，编写好values.yaml后直接部署到集群即可，会自动创建CronJob用于定时更新

## 使用Docker

### 直接运行Job

将jobs.yaml和config.yaml文件放置在同一目录下，然后执行如下命令

```shell
docker run -d \
-v $(pwd)/config.yaml:/code/app/config/config.yaml \
-v $(pwd)/jobs.yaml:/code/app/config/jobs.yaml \
tushare_integration:latest python main.py run job daily_morning
```

### 使用Crontab定时运行Job

将jobs.yaml和config.yaml文件放置在同一目录下，然后在crontab中添加上述命令
