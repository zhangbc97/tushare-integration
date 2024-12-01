# 故障排除指南

本文档列举了使用过程中常见的问题和解决方案。

## 常见错误

### 1. 数据库连接问题

#### 症状
- 无法连接到数据库
- 数据库连接超时
- 权限错误

#### 解决方案
1. 检查数据库配置
   ```yaml
   database:
     host: '127.0.0.1'  # 确保IP地址正确
     port: '8123'       # 确保端口号正确
     user: 'default'    # 检查用户名
     password: ''       # 检查密码
   ```

2. 检查数据库服务状态
   ```bash
   # 对于Docker部署
   docker ps | grep clickhouse
   docker logs clickhouse-server
   
   # 对于本地部署
   systemctl status clickhouse-server
   ```

3. 检查网络连接
   ```bash
   telnet 127.0.0.1 8123
   ```

### 2. Tushare API问题

#### 症状
- API调用失败
- 频率限制错误
- 权限不足

#### 解决方案
1. 检查Token配置
   ```yaml
   tushare_token: 'your_token'  # 确保Token正确
   ```

2. 检查积分设置
   ```yaml
   tushare_point: 2000  # 确保与实际积分匹配
   ```

3. 调整并发设置
   ```yaml
   concurrent_requests: 1  # 降低并发请求数
   ```

### 3. 数据同步问题

#### 症状
- 数据不完整
- 数据重复
- 同步速度慢

#### 解决方案
1. 检查表结构
   ```sql
   -- Clickhouse
   SHOW CREATE TABLE stock_basic;
   
   -- MySQL
   DESCRIBE stock_basic;
   ```

2. 检查数据一致性
   ```sql
   -- 检查重复数据
   SELECT ts_code, COUNT(*) 
   FROM stock_basic 
   GROUP BY ts_code 
   HAVING COUNT(*) > 1;
   ```

3. 优化同步性能
   - 增加 `concurrent_items` 值
   - 使用并行模式：`parallel_mode: true`
   - 调整批量写入大小

### 4. Docker相关问题

#### 症状
- 容器启动失败
- 容器无法访问网络
- 数据持久化失败

#### 解决方案
1. 检查Docker日志
   ```bash
   docker logs tushare-integration
   ```

2. 检查数据卷挂载
   ```bash
   docker inspect clickhouse-server
   ```

3. 检查网络配置
   ```bash
   docker network ls
   docker network inspect bridge
   ```

## 日志收集

### 查看日志
1. Docker环境
   ```bash
   docker logs -f tushare-integration
   ```

2. 本地环境
   ```bash
   tail -f logs/tushare_integration.log
   ```

### 日志级别调整
在 `config.yaml` 中设置：
```yaml
log_level: DEBUG  # 可选值：DEBUG, INFO, WARNING, ERROR
```

## 性能优化建议

1. 数据库优化
   - 使用SSD存储
   - 增加系统内存
   - 优化数据库配置

2. 网络优化
   - 使用内网部署
   - 确保网络稳定性
   - 使用合适的并发设置

3. 应用优化
   - 使用增量更新
   - 合理设置批次大小
   - 避免高峰期同步

## 获取帮助

如果上述方案无法解决您的问题：

1. 查看[项目文档](https://github.com/zhangbc/tushare-integration)
2. 提交[Issue](https://github.com/zhangbc/tushare-integration/issues)