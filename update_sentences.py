#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import re
import sys

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

def get_sentences_from_db(conn):
    """从数据库获取所有句子"""
    sentences_dict = {}
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, sentence FROM corpus_sentences ORDER BY id")
            for row in cursor:
                sentences_dict[row[0]] = row[1]
        return sentences_dict
    except Exception as e:
        print(f"获取数据库句子失败: {e}")
        return {}

def read_original_file(filename):
    """读取原始文件内容"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        print(f"读取文件失败: {e}")
        return []

def update_sentences(original_lines, db_sentences):
    """更新句子内容"""
    updated_lines = []
    pattern = re.compile(r'^(\d+)\.\s*(.*)$')
    
    for line in original_lines:
        line = line.strip()
        if not line:
            updated_lines.append('')
            continue
            
        # 跳过包含"保持原样"的行
        if "保持原样" in line:
            updated_lines.append(line)
            continue
            
        # 匹配id和内容
        match = pattern.match(line)
        if match:
            sentence_id = int(match.group(1))
            # 从数据库获取对应的句子内容
            if sentence_id in db_sentences:
                updated_line = f"{sentence_id}. {db_sentences[sentence_id]}"
                updated_lines.append(updated_line)
            else:
                # 如果数据库中找不到对应的id，保持原样
                updated_lines.append(line)
        else:
            # 如果不是以数字开头的行，保持原样
            updated_lines.append(line)
    
    return updated_lines

def save_updated_file(filename, content):
    """保存更新后的文件"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        print(f"文件已成功更新并保存为: {filename}")
    except Exception as e:
        print(f"保存文件失败: {e}")

def main():
    # 连接到数据库
    print("正在连接到数据库...")
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # 获取数据库中的句子
        print("正在从数据库获取句子数据...")
        db_sentences = get_sentences_from_db(conn)
        if not db_sentences:
            print("数据库中没有找到句子数据")
            return
        
        print(f"从数据库获取到 {len(db_sentences)} 条句子")
        
        # 读取原始文件
        original_file = "待更新句子"
        print(f"正在读取文件: {original_file}")
        original_lines = read_original_file(original_file)
        if not original_lines:
            print("原始文件为空或读取失败")
            return
        
        # 更新句子内容
        print("正在更新句子内容...")
        updated_content = update_sentences(original_lines, db_sentences)
        
        # 保存更新后的文件
        output_file = "待更新句子_已更新"
        save_updated_file(output_file, updated_content)
        
    finally:
        conn.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    main()
