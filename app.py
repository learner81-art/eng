from flask import Flask, jsonify, render_template
import pymysql
import re

app = Flask(__name__)

def highlight_grammar(text):
    # 高亮复数形式
    text = re.sub(r'(\w+)(s|es)\b', r'<span class="highlight">\1\2</span>', text)
    # 高亮动词时态
    text = re.sub(r'(\w+)(ed|ing)\b', r'<span class="highlight">\1\2</span>', text)
    return text

@app.route('/api/sentences')
def get_sentences():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='root',
        database='corpus_db'
    )
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, sentence FROM corpus_sentences")
            sentences = []
            for row in cursor:
                sentences.append({
                    'id': row[0],
                    'sentence': highlight_grammar(row[1])
                })
            return jsonify(sentences)
    finally:
        conn.close()

@app.route('/')
def index():
    return render_template('corpus_visualized.html')

if __name__ == '__main__':
    app.run(port=5057, debug=False, host='0.0.0.0')
