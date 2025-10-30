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

def read_translation_file(filename):
    """读取翻译文件，返回id到翻译的字典"""
    translations = {}
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式匹配 "数字. 翻译内容" 格式
        pattern = re.compile(r'^(\d+)\.\s+(.+)$', re.MULTILINE)
        matches = pattern.findall(content)
        
        for match in matches:
            sentence_id = int(match[0])
            translation = match[1].strip()
            translations[sentence_id] = translation
        
        print(f"从文件中读取到 {len(translations)} 条翻译")
        return translations
        
    except Exception as e:
        print(f"读取翻译文件失败: {e}")
        return {}

def update_database_translations(conn, translations):
    """更新数据库中的翻译字段"""
    try:
        with conn.cursor() as cursor:
            updated_count = 0
            error_count = 0
            
            for sentence_id, translation in translations.items():
                try:
                    # 更新对应id的translation字段
                    sql = "UPDATE corpus_sentences SET translation = %s WHERE id = %s"
                    cursor.execute(sql, (translation, sentence_id))
                    updated_count += 1
                    print(f"已更新ID {sentence_id} 的翻译")
                    
                except Exception as e:
                    print(f"更新ID {sentence_id} 失败: {e}")
                    error_count += 1
            
            # 提交事务
            conn.commit()
            print(f"\n更新完成: 成功 {updated_count} 条, 失败 {error_count} 条")
            
    except Exception as e:
        print(f"更新数据库失败: {e}")
        conn.rollback()

def verify_updates(conn, translations):
    """验证更新结果"""
    try:
        with conn.cursor() as cursor:
            verified_count = 0
            error_count = 0
            
            for sentence_id, expected_translation in translations.items():
                cursor.execute("SELECT translation FROM corpus_sentences WHERE id = %s", (sentence_id,))
                result = cursor.fetchone()
                
                if result and result[0] == expected_translation:
                    verified_count += 1
                else:
                    error_count += 1
                    print(f"验证失败: ID {sentence_id}")
            
            print(f"\n验证结果: 成功 {verified_count} 条, 失败 {error_count} 条")
            
    except Exception as e:
        print(f"验证更新失败: {e}")

def main():
    print("开始更新数据库翻译字段...")
    
    # 连接到数据库
    print("正在连接到数据库...")
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # 读取翻译文件
        translation_file = "待更新句子中文"
        print(f"正在读取翻译文件: {translation_file}")
        translations = read_translation_file(translation_file)
        
        if not translations:
            print("没有读取到翻译数据，请检查文件格式")
            return
        
        # 更新数据库
        print("正在更新数据库...")
        update_database_translations(conn, translations)
        
        # 验证更新结果
        print("\n正在验证更新结果...")
        verify_updates(conn, translations)
        
    finally:
        conn.close()
        print("\n数据库连接已关闭")

if __name__ == "__main__":
    main()
