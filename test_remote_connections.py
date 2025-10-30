#!/usr/bin/env python3
"""
测试远程Redis和MySQL连接
"""

import redis
import pymysql

def test_redis_connection():
    """测试远程Redis连接"""
    print("🔗 测试远程Redis连接...")
    try:
        r = redis.Redis(
            host='127.0.0.1',
            port=6379,
            db=0,
            password='redis123',
            decode_responses=True
        )
        r.ping()
        print("✅ Redis连接成功")
        
        # 测试数据读写
        test_key = "connection_test"
        test_value = "Hello from remote Redis!"
        r.set(test_key, test_value)
        result = r.get(test_key)
        print(f"📝 测试数据读写: {result}")
        
        # 列出所有键
        keys = r.keys('*')
        print(f"📊 Redis中的键数量: {len(keys)}")
        if keys:
            print(f"🔑 键列表: {keys[:10]}{'...' if len(keys) > 10 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return False

def test_mysql_connection():
    """测试远程MySQL连接"""
    print("\n🔗 测试远程MySQL连接...")
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='root',
            database='corpus_db'
        )
        
        with conn.cursor() as cursor:
            # 测试查询
            cursor.execute("SELECT COUNT(*) FROM corpus_sentences")
            count = cursor.fetchone()[0]
            print(f"✅ MySQL连接成功")
            print(f"📊 句子表记录数: {count}")
            
            # 显示数据库列表
            cursor.execute("SHOW DATABASES")
            databases = [db[0] for db in cursor.fetchall()]
            print(f"🗄️  数据库列表: {databases}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        return False

def main():
    print("🚀 开始测试远程连接...")
    print("=" * 50)
    
    redis_success = test_redis_connection()
    mysql_success = test_mysql_connection()
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"✅ Redis连接: {'成功' if redis_success else '失败'}")
    print(f"✅ MySQL连接: {'成功' if mysql_success else '失败'}")
    
    if redis_success and mysql_success:
        print("\n🎉 所有远程连接测试通过!")
    else:
        print("\n❌ 部分连接测试失败，请检查配置")

if __name__ == "__main__":
    main()
