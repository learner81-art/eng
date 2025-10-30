#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
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
        print("数据库连接成功")
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def execute_sql_statements(conn, sql_statements):
    """执行SQL语句"""
    success_count = 0
    error_count = 0
    
    try:
        with conn.cursor() as cursor:
            for sql in sql_statements:
                try:
                    cursor.execute(sql)
                    success_count += 1
                    print(f"执行成功: {sql[:100]}...")  # 显示前100个字符
                except Exception as e:
                    error_count += 1
                    print(f"执行失败: {sql[:100]}...")
                    print(f"错误信息: {e}")
        
        # 提交事务
        conn.commit()
        print(f"\n执行完成: 成功 {success_count} 条, 失败 {error_count} 条")
        return success_count, error_count
        
    except Exception as e:
        conn.rollback()
        print(f"执行过程中发生错误: {e}")
        return success_count, error_count

def read_original_file(filename):
    """读取原始文件内容"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return []

def generate_update_statements(original_lines):
    """生成MySQL UPDATE语句"""
    update_statements = []
    pattern = re.compile(r'^(\d+)\.\s*(.*)$')
    
    for line in original_lines:
        line = line.strip()
        if not line:
            continue
            
        # 跳过包含"保持原样"的行
        if "保持原样" in line:
            print(f"跳过: {line}")
            continue
            
        # 匹配id和内容
        match = pattern.match(line)
        if match:
            sentence_id = int(match.group(1))
            new_content = match.group(2)
            
            # 转义单引号
            escaped_content = new_content.replace("'", "\\'")
            update_sql = f"UPDATE corpus_sentences SET sentence = '{escaped_content}' WHERE id = {sentence_id};"
            update_statements.append(update_sql)
            print(f"生成UPDATE语句: ID {sentence_id}")
            print(f"  新内容: {new_content}")
            print(f"  SQL: {update_sql}")
            print()
        else:
            # 如果不是以数字开头的行，跳过
            if line and not line.startswith('以下是严格按照原始句子顺序'):
                print(f"跳过非句子行: {line}")
    
    return update_statements

def save_sql_to_file(filename, sql_statements):
    """保存SQL语句到文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('-- MySQL UPDATE语句 - 根据待更新句子文件生成\n')
            f.write('-- 执行前请仔细检查每条语句\n\n')
            for sql in sql_statements:
                f.write(sql + '\n')
        print(f"SQL语句已保存到: {filename}")
    except Exception as e:
        print(f"保存SQL文件失败: {e}")

def main():
    # 连接到数据库
    print("正在连接到数据库...")
    conn = connect_to_database()
    if not conn:
        print("无法连接到数据库，程序退出")
        return
    
    try:
        # 读取原始文件
        original_file = "待更新句子"
        print(f"正在读取文件: {original_file}")
        original_lines = read_original_file(original_file)
        if not original_lines:
            print("原始文件为空或读取失败")
            return
        
        # 生成UPDATE语句
        print("正在生成UPDATE语句...")
        update_statements = generate_update_statements(original_lines)
        
        if update_statements:
            print(f"\n共生成 {len(update_statements)} 条UPDATE语句")
            
            # 询问用户是否要执行SQL语句
            print("\n是否要立即执行这些UPDATE语句？(y/n)")
            choice = input().strip().lower()
            
            if choice == 'y' or choice == 'yes':
                print("开始执行UPDATE语句...")
                success_count, error_count = execute_sql_statements(conn, update_statements)
                
                # 保存SQL语句到文件（用于备份和检查）
                sql_file = "update_sentences.sql"
                save_sql_to_file(sql_file, update_statements)
                print(f"\nSQL语句已备份到: {sql_file}")
                
                if error_count == 0:
                    print("所有UPDATE语句执行成功！")
                else:
                    print(f"有 {error_count} 条语句执行失败，请检查错误信息")
            else:
                # 用户选择不执行，只保存到文件
                sql_file = "update_sentences.sql"
                save_sql_to_file(sql_file, update_statements)
                print(f"SQL语句已保存到: {sql_file}")
                print("您可以在确认无误后手动执行这些语句")
        else:
            print("\n没有需要更新的句子")
        
    finally:
        conn.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    main()
