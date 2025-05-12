import re
import pymysql

def process_corpus():
    # 连接到MySQL容器
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='root',
        database='corpus_db'
    )

    try:
        # 读取corpus文件内容
        with open('corpus', 'r', encoding='utf-8') as f:
            content = f.read()

        # 分割句子 - 以句号、问号或感叹号作为句子结束标志
        sentences = re.split(r'(?<=[.!?])\s+', content)

        # 插入数据库
        with conn.cursor() as cursor:
            for sentence in sentences:
                if sentence.strip():  # 跳过空句子
                    # 去除句子前后的空白字符
                    clean_sentence = sentence.strip()
                    # 使用参数化查询避免SQL注入
                    cursor.execute(
                        "INSERT INTO corpus_sentences (sentence) VALUES (%s)",
                        (clean_sentence,)
                    )
            
            conn.commit()
            print(f'成功插入 {len(sentences)} 条句子到数据库')

    except Exception as e:
        print(f"处理过程中发生错误: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    process_corpus()
