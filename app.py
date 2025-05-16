from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO, emit
import pymysql
import re
import redis
import json
import datetime

app = Flask(__name__)
socketio = SocketIO(app, 
                  cors_allowed_origins="*", 
                  async_mode='eventlet',
                  logger=True,
                  engineio_logger=True,
                  transports=['websocket', 'polling'])
r = redis.Redis(host='localhost', port=6379, db=0)

# 30天缓存时间(秒)
CACHE_EXPIRE = 86400*30

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

@app.route('/api/get_saved_data', methods=['GET'])
def get_saved_data():
    saved_text = r.get('corpus_input') or b''
    if not saved_text:
        return jsonify({
            'status': 'success',
            'data': None,
            'message': '没有找到保存的数据'
        })
    
    decoded_text = saved_text.decode('utf-8')
    try:
        # 尝试解析为JSON，如果失败则返回原始文本
        data = json.loads(decoded_text)
        return jsonify({
            'status': 'success',
            'data': data if isinstance(data, dict) else decoded_text,
            'is_json': isinstance(data, dict)
        })
    except json.JSONDecodeError:
        return jsonify({
            'status': 'success',
            'data': decoded_text,
            'is_json': False
        })

@app.route('/api/save_input', methods=['POST'])
def save_input():
    try:
        # 记录请求开始
        print(f"\n[保存请求开始] {datetime.datetime.now().isoformat()}")
        
        # 获取原始POST数据
        raw_data = request.get_data(as_text=True)
        print(f"[原始请求数据] {raw_data[:200]}...")  # 限制日志长度
        
        if not raw_data:
            print("[错误] 请求数据为空")
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400
        
        # 尝试解析为JSON
        try:
            data = json.loads(raw_data)
            text = data.get('text', raw_data)
            print(f"[解析后的数据] text字段: {text[:100]}...")  # 限制日志长度
        except json.JSONDecodeError as je:
            text = raw_data
            print(f"[JSON解析警告] 使用原始文本: {je}")
        
        # 保存文本内容到Redis
        print(f"[保存到Redis] 键: corpus_input, 过期时间: {CACHE_EXPIRE}秒")
        r.setex('corpus_input', CACHE_EXPIRE, text)
        
        # 记录成功
        print(f"[保存成功] {datetime.datetime.now().isoformat()}")
        return jsonify({'status': 'success'})
        
    except Exception as e:
        print(f"[保存错误] {type(e).__name__}: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/test_redis', methods=['GET'])
def test_redis():
    try:
        # 测试Redis连接
        r.ping()
        
        # 测试数据读写
        test_key = "redis_test_key"
        test_data = {"test": "Redis connection is working"}
        r.set(test_key, json.dumps(test_data))
        saved_data = r.get(test_key)
        
        return jsonify({
            'status': 'success',
            'data': json.loads(saved_data) if saved_data else None
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    print('客户端已连接')
    emit('connection_response', {'data': '连接成功'})

@socketio.on('disconnect')
def handle_disconnect():
    print('客户端已断开')

@socketio.on('message')
def handle_message(message):
    print('收到消息:', message)
    # 将消息存入Redis，使用与API相同的过期时间
    # 同时保存到websocket_message和corpus_input键
    json_message = json.dumps(message)
    r.setex('websocket_message', CACHE_EXPIRE, json_message)
    r.setex('corpus_input', CACHE_EXPIRE, json_message)
    emit('message_response', {'status': 'success'})

@socketio.on('get_redis_data')
def handle_get_redis_data(data):
    key = data.get('key')
    if key:
        value = r.get(key)
        # 如果key存在但值为空，从Redis删除该key
        if value is None and r.exists(key):
            r.delete(key)
        emit('redis_data', {'key': key, 'value': value.decode() if value else None})

if __name__ == '__main__':
    socketio.run(app, port=5057, debug=False, host='0.0.0.0')
