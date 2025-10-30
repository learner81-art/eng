#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql

def connect_to_database():
    """连接到MySQL数据库"""
    try:
        conn = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='root',
            password='root',
            database='corpus_db',
            charset='utf8mb4'
        )
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def check_table_structure(conn):
    """查看corpus_sentences表的结构"""
    try:
        with conn.cursor() as cursor:
            # 查看表结构
            cursor.execute("DESCRIBE corpus_sentences")
            print("corpus_sentences表结构:")
            print("-" * 50)
            for row in cursor:
                print(f"字段名: {row[0]}, 类型: {row[1]}, 是否为空: {row[2]}, 键: {row[3]}, 默认值: {row[4]}, 额外: {row[5]}")
            print("-" * 50)
            
            # 查看表中有多少条记录
            cursor.execute("SELECT COUNT(*) FROM corpus_sentences")
            count = cursor.fetchone()[0]
            print(f"表中总记录数: {count}")
            
            # 查看前几条记录，了解数据格式
            cursor.execute("SELECT * FROM corpus_sentences LIMIT 5")
            print("\n前5条记录示例:")
            print("-" * 50)
            for row in cursor:
                print(row)
            print("-" * 50)
            
    except Exception as e:
        print(f"查看表结构失败: {e}")

def main():
    print("正在连接到数据库...")
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        check_table_structure(conn)
    finally:
        conn.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    main()
