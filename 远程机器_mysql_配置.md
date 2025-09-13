# 远程机器 MySQL 配置文档

## 服务器信息
- **IP地址**: 192.168.3.242
- **MySQL版本**: 9.4.0
- **主机名**: MacdeMacBook-Pro.local
- **连接用户**: root
- **密码**: root
- **端口**: 3306

## 连接测试状态
✅ **连接成功** - 已验证可以正常连接和查询

## 数据库列表 (共14个)
1. corpus_db
2. coze_chat
3. coze_chat_copy
4. douyin_downloader
5. douyin_media_processor
6. filter
7. information_schema
8. mysql
9. performance_schema
10. sys
11. **ted_talks_db** (项目主数据库)
12. ted_talks_db_bak
13. video_generation_db
14. video_platform_db

## ted_talks_db 数据库结构

### 核心表 (18个表)

#### 1. 演讲者相关表
- **speakers** - 演讲者信息表 (10列)
  - id, english_name, chinese_name, 等字段
- **speakers_speaker** - 演讲者扩展表 (4列)
  - id, name, bio, 等字段

#### 2. 演讲内容相关表
- **talks** - 演讲主表 (15列)
  - id, speaker_id, speaker_name_zh, 等字段
- **talk_speakers** - 演讲-演讲者关联表 (2列)
  - talk_id, speaker_id

#### 3. NLP处理相关表
- **raw_texts** - 原始文本表 (5列)
  - text_id, task_id, original_content, 等字段
- **filtered_results** - 过滤结果表 (5列)
  - result_id, text_id, processed_content, 等字段
- **nlp_tasks** - NLP任务表 (5列)
  - task_id, task_name, created_at, 等字段
- **synonym_mappings** - 同义词映射表 (4列)
  - mapping_id, base_word, synonym, 等字段

#### 4. Django框架表
- auth_group, auth_group_permissions, auth_permission
- auth_user, auth_user_groups, auth_user_user_permissions  
- django_admin_log, django_content_type, django_migrations, django_session

## 用户权限配置
```sql
-- 当前权限配置 (已验证)
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root';
FLUSH PRIVILEGES;
```

## 连接脚本工具

已创建以下连接工具：

### 1. 基础连接测试
```bash
python3 simple_db_test.py
```

### 2. 完整连接管理
```bash
python3 db_connection_manager.py
```

### 3. 高级查询工具
```bash
python3 test_db_query.py
```

### 4. 权限修复工具
```bash
python3 fix_db_connection.py
```

### 5. SSH隧道连接 (备用方案)
```bash
chmod +x mysql_ssh_tunnel.sh
./mysql_ssh_tunnel.sh
```

## 网络配置要求

### 防火墙规则
- 允许出站连接: 3306/tcp
- 允许入站连接: 3306/tcp (如果需要在远程机器上提供服务)

### 连接测试命令
```bash
# 测试网络连通性
ping 192.168.3.242

# 测试端口开放
nc -zv 192.168.3.242 3306

# 或者使用telnet
telnet 192.168.3.242 3306
```

## 性能指标
- **服务器运行时间**: 1124秒 (测试时)
- **当前连接数**: 4个进程
- **总记录数**: 405条 (talks表)

## 备份建议
```bash
# 定期备份ted_talks_db
mysqldump -h 192.168.3.242 -u root -p ted_talks_db > ted_talks_backup_$(date +%Y%m%d).sql

# 备份所有数据库
mysqldump -h 192.168.3.242 -u root -p --all-databases > full_mysql_backup_$(date +%Y%m%d).sql
```

## 监控建议
```sql
-- 监控连接状态
SHOW PROCESSLIST;

-- 监控数据库大小
SELECT table_schema "Database", 
ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) "Size (MB)" 
FROM information_schema.tables 
GROUP BY table_schema;

-- 监控表大小
SELECT table_name, 
ROUND((data_length + index_length) / 1024 / 1024, 2) "Size (MB)"
FROM information_schema.tables 
WHERE table_schema = 'ted_talks_db'
ORDER BY (data_length + index_length) DESC;
```

## 故障排除

### 常见问题
1. **连接被拒绝**: 检查防火墙和MySQL权限
2. **权限错误**: 运行fix_db_connection.py修复
3. **网络问题**: 使用SSH隧道备用方案

### 日志检查
```bash
# 查看MySQL错误日志
tail -f /var/log/mysql/error.log

# 或者通用日志位置
tail -f /var/log/mysqld.log
```

---
*最后更新: 2025-09-11*
*测试状态: ✅ 连接正常*
