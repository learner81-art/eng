#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pymysql
import re

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

def parse_sentences_file(filename):
    """解析待更新句子中文10.30文件，提取中英文句子对"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 分割中文部分和英文部分
        parts = content.split('## 英文部分')
        if len(parts) != 2:
            print("文件格式不正确，无法找到中英文部分分隔")
            return []
        
        chinese_part = parts[0].replace('## 中文部分', '').strip()
        english_part = parts[1].strip()
        
        # 解析中文句子
        chinese_sentences = []
        chinese_pattern = re.compile(r'^\d+\.\s*(.+)$', re.MULTILINE)
        for match in chinese_pattern.finditer(chinese_part):
            chinese_sentences.append(match.group(1).strip())
        
        # 解析英文句子
        english_sentences = []
        english_pattern = re.compile(r'^\d+\.\s*(.+)$', re.MULTILINE)
        for match in english_pattern.finditer(english_part):
            english_sentences.append(match.group(1).strip())
        
        # 检查数量是否匹配
        if len(chinese_sentences) != len(english_sentences):
            print(f"中英文句子数量不匹配: 中文{len(chinese_sentences)}条, 英文{len(english_sentences)}条")
            return []
        
        # 组合成句子对
        sentence_pairs = []
        for i in range(len(chinese_sentences)):
            sentence_pairs.append({
                'english': english_sentences[i],
                'chinese': chinese_sentences[i]
            })
        
        print(f"成功解析 {len(sentence_pairs)} 对中英文句子")
        return sentence_pairs
        
    except Exception as e:
        print(f"解析文件失败: {e}")
        return []

def insert_sentences_to_db(conn, sentence_pairs):
    """将句子对插入到数据库"""
    try:
        with conn.cursor() as cursor:
            inserted_count = 0
            for pair in sentence_pairs:
                # 检查是否已存在相同的英文句子
                cursor.execute("SELECT id FROM corpus_sentences WHERE sentence = %s", (pair['english'],))
                existing = cursor.fetchone()
                
                if existing:
                    print(f"句子已存在，跳过: {pair['english'][:50]}...")
                    continue
                
                # 插入新句子
                cursor.execute(
                    "INSERT INTO corpus_sentences (sentence, translation) VALUES (%s, %s)",
                    (pair['english'], pair['chinese'])
                )
                inserted_count += 1
                print(f"插入句子: {pair['english'][:50]}...")
            
            conn.commit()
            print(f"成功插入 {inserted_count} 条新句子")
            return inserted_count
            
    except Exception as e:
        print(f"插入句子到数据库失败: {e}")
        conn.rollback()
        return 0

def main():
    print("开始处理待更新句子中文10.30文件...")
    
    # 连接到数据库
    print("正在连接到数据库...")
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # 解析文件
        filename = "待更新句子中文10.30"
        print(f"正在解析文件: {filename}")
        sentence_pairs = parse_sentences_file(filename)
        if not sentence_pairs:
            print("没有解析到有效的句子对")
            return
        
        # 插入到数据库
        print("正在将句子插入到数据库...")
        inserted_count = insert_sentences_to_db(conn, sentence_pairs)
        
        print(f"\n处理完成！成功插入了 {inserted_count} 条新句子到数据库")
        
    finally:
        conn.close()
        print("数据库连接已关闭")

if __name__ == "__main__":
    main()
