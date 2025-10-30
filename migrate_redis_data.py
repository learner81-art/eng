#!/usr/bin/env python3
"""
Redis数据迁移脚本
将本地Redis数据迁移到远程Redis服务器
"""

import redis
import json
import argparse
from tqdm import tqdm

def migrate_redis_data(local_host='localhost', local_port=6379, local_db=0, local_password=None,
                      remote_host='127.0.0.1', remote_port=6379, remote_db=0, remote_password='redis123'):
    """
    迁移Redis数据从本地到远程
    
    Args:
        local_host: 本地Redis主机
        local_port: 本地Redis端口
        local_db: 本地Redis数据库
        local_password: 本地Redis密码
        remote_host: 远程Redis主机
        remote_port: 远程Redis端口
        remote_db: 远程Redis数据库
        remote_password: 远程Redis密码
    """
    
    print("🚀 开始Redis数据迁移...")
    print(f"📡 源: {local_host}:{local_port} (DB {local_db})")
    print(f"📡 目标: {remote_host}:{remote_port} (DB {remote_db})")
    print("-" * 50)
    
    try:
        # 连接到本地Redis
        print("🔗 连接到本地Redis...")
        local_redis = redis.Redis(
            host=local_host,
            port=local_port,
            db=local_db,
            password=local_password,
            decode_responses=True
        )
        local_redis.ping()
        print("✅ 本地Redis连接成功")
        
        # 连接到远程Redis
        print("🔗 连接到远程Redis...")
        remote_redis = redis.Redis(
            host=remote_host,
            port=remote_port,
            db=remote_db,
            password=remote_password,
            decode_responses=True
        )
        remote_redis.ping()
        print("✅ 远程Redis连接成功")
        
        # 获取所有键
        print("📋 获取所有键...")
        all_keys = local_redis.keys('*')
        print(f"📊 找到 {len(all_keys)} 个键")
        
        if not all_keys:
            print("❌ 本地Redis中没有数据可迁移")
            return
        
        migrated_count = 0
        error_count = 0
        
        # 迁移数据
        print("🔄 开始迁移数据...")
        for key in tqdm(all_keys, desc="迁移进度"):
            try:
                # 获取键的类型
                key_type = local_redis.type(key)
                
                if key_type == 'string':
                    # 字符串类型
                    value = local_redis.get(key)
                    ttl = local_redis.ttl(key)
                    if ttl > 0:
                        remote_redis.setex(key, ttl, value)
                    else:
                        remote_redis.set(key, value)
                
                elif key_type == 'hash':
                    # 哈希类型
                    hash_data = local_redis.hgetall(key)
                    remote_redis.hset(key, mapping=hash_data)
                    ttl = local_redis.ttl(key)
                    if ttl > 0:
                        remote_redis.expire(key, ttl)
                
                elif key_type == 'list':
                    # 列表类型
                    list_data = local_redis.lrange(key, 0, -1)
                    if list_data:
                        remote_redis.rpush(key, *list_data)
                    ttl = local_redis.ttl(key)
                    if ttl > 0:
                        remote_redis.expire(key, ttl)
                
                elif key_type == 'set':
                    # 集合类型
                    set_data = local_redis.smembers(key)
                    if set_data:
                        remote_redis.sadd(key, *set_data)
                    ttl = local_redis.ttl(key)
                    if ttl > 0:
                        remote_redis.expire(key, ttl)
                
                elif key_type == 'zset':
                    # 有序集合类型
                    zset_data = local_redis.zrange(key, 0, -1, withscores=True)
                    if zset_data:
                        for member, score in zset_data:
                            remote_redis.zadd(key, {member: score})
                    ttl = local_redis.ttl(key)
                    if ttl > 0:
                        remote_redis.expire(key, ttl)
                
                migrated_count += 1
                
            except Exception as e:
                print(f"\n❌ 迁移键 '{key}' 时出错: {e}")
                error_count += 1
        
        print("\n" + "=" * 50)
        print("📊 迁移完成!")
        print(f"✅ 成功迁移: {migrated_count} 个键")
        print(f"❌ 迁移失败: {error_count} 个键")
        print(f"📈 成功率: {(migrated_count/(migrated_count+error_count))*100:.1f}%")
        
        # 验证迁移结果
        print("\n🔍 验证迁移结果...")
        remote_keys_count = len(remote_redis.keys('*'))
        print(f"📊 远程Redis中的键数量: {remote_keys_count}")
        
        if remote_keys_count == len(all_keys):
            print("✅ 验证成功: 所有键都已迁移")
        else:
            print(f"⚠️  验证警告: 本地有 {len(all_keys)} 个键，远程有 {remote_keys_count} 个键")
        
    except redis.ConnectionError as e:
        print(f"❌ Redis连接错误: {e}")
    except Exception as e:
        print(f"❌ 迁移过程中发生错误: {e}")
    finally:
        # 关闭连接
        try:
            local_redis.close()
            remote_redis.close()
        except:
            pass

def main():
    parser = argparse.ArgumentParser(description='Redis数据迁移工具')
    parser.add_argument('--local-host', default='localhost', help='本地Redis主机')
    parser.add_argument('--local-port', type=int, default=6379, help='本地Redis端口')
    parser.add_argument('--local-db', type=int, default=0, help='本地Redis数据库')
    parser.add_argument('--local-password', help='本地Redis密码')
    parser.add_argument('--remote-host', default='192.168.3.242', help='远程Redis主机')
    parser.add_argument('--remote-port', type=int, default=6379, help='远程Redis端口')
    parser.add_argument('--remote-db', type=int, default=0, help='远程Redis数据库')
    parser.add_argument('--remote-password', default='redis123', help='远程Redis密码')
    
    args = parser.parse_args()
    
    migrate_redis_data(
        local_host=args.local_host,
        local_port=args.local_port,
        local_db=args.local_db,
        local_password=args.local_password,
        remote_host=args.remote_host,
        remote_port=args.remote_port,
        remote_db=args.remote_db,
        remote_password=args.remote_password
    )

if __name__ == "__main__":
    main()
