from flask import Flask, jsonify, render_template, request
import pymysql
import re
import redis
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)
r = redis.Redis(host='localhost', port=6379, db=0)

# 30天缓存时间(秒)
CACHE_EXPIRE = 2592000

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
    # 尝试从Redis加载保存的内容
    saved_text = r.get('corpus_input') or b''
    return render_template('corpus_visualized.html', saved_text=saved_text.decode('utf-8'))

@socketio.on('save_input')
def handle_save_input(json):
    text = json['text']
    r.setex('corpus_input', CACHE_EXPIRE, text)
    emit('saved', {'status': 'success'})

if __name__ == '__main__':
    app.run(port=5057, debug=False, host='0.0.0.0')
