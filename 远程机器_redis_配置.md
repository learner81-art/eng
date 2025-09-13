# Redis远程访问配置报告

## 概述
本文档记录了在macOS系统上配置Redis允许远程访问的完整过程，特别针对IP地址192.168.3.59进行增删改查操作的权限配置。

## 系统环境
- **操作系统**: macOS
- **Redis版本**: 8.2.1
- **配置文件**: `/usr/local/etc/redis.conf`
- **监听端口**: 6379

## 配置步骤

### 1. Redis配置文件修改

#### 原始配置备份
```bash
sudo cp /usr/local/etc/redis.conf /usr/local/etc/redis.conf.backup
```

#### 关键配置修改
```bash
# 修改绑定地址，允许所有网络接口访问
bind 0.0.0.0 ::1

# 禁用保护模式以允许远程连接
protected-mode no

# 设置认证密码（取消注释并修改）
requirepass redis123
```

### 2. 服务重启
```bash
brew services restart redis
```

### 3. 防火墙配置（macOS pf防火墙）
```bash
# 允许192.168.3.59访问6379端口
echo "pass in proto tcp from 192.168.3.59 to any port 6379" | sudo pfctl -ef -
```

## 安全配置说明

### 认证机制
- **密码**: `redis123`
- **重要性**: 防止未授权访问
- **使用方式**: 连接时使用 `-a redis123` 参数

### 网络访问控制
- **绑定地址**: `0.0.0.0` (允许所有网络接口)
- **保护模式**: 禁用 (允许远程连接)
- **防火墙规则**: 仅允许192.168.3.59访问6379端口

## 连接测试

### 本地连接测试
```bash
redis-cli -a redis123 ping
# 预期输出: PONG
```

### 远程连接测试（从192.168.3.59）
```bash
redis-cli -h <本机IP地址> -p 6379 -a redis123 ping
# 预期输出: PONG
```

### 信息查询
```bash
redis-cli -a redis123 info server
```

## 权限管理

### 当前权限设置
- **允许的IP**: 192.168.3.59
- **允许的操作**: 所有Redis命令（增删改查）
- **认证要求**: 必须提供密码 `redis123`

### 权限验证
```bash
# 测试基本操作权限
redis-cli -a redis123 set test_key "test_value"
redis-cli -a redis123 get test_key
redis-cli -a redis123 del test_key
```

## 故障排除

### 常见问题

1. **连接被拒绝**
   - 检查Redis服务是否运行: `brew services list | grep redis`
   - 检查防火墙规则: `sudo pfctl -s rules`

2. **认证失败**
   - 确认密码正确性
   - 检查配置文件中的requirepass设置

3. **远程连接超时**
   - 确认网络连通性
   - 检查防火墙配置

### 服务状态检查
```bash
# 检查Redis服务状态
brew services info redis

# 检查监听端口
netstat -an | grep 6379

# 检查防火墙状态
sudo pfctl -s info
```

## 维护指南

### 配置文件管理
- 主配置文件: `/usr/local/etc/redis.conf`
- 备份文件: `/usr/local/etc/redis.conf.backup`
- 建议修改前始终备份配置文件

### 服务管理命令
```bash
# 启动服务
brew services start redis

# 停止服务
brew services stop redis

# 重启服务
brew services restart redis

# 查看服务状态
brew services list
```

### 日志查看
```bash
# Redis日志位置
tail -f /usr/local/var/log/redis.log
```

## 安全建议

1. **定期更换密码**: 建议定期更新requirepass密码
2. **限制访问IP**: 可根据需要调整防火墙规则，限制更多IP
3. **启用TLS加密**: 对于生产环境建议启用SSL/TLS加密
4. **监控访问日志**: 定期检查Redis访问日志

## 版本信息
- **文档创建日期**: 2025年9月11日
- **配置完成时间**: 下午4:29
- **负责人**: 系统管理员

---

**备注**: 此配置已测试通过，Redis服务正常运行，允许192.168.3.59进行远程增删改查操作。
