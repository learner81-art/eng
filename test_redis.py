import redis
import json
import socketio
import time
import requests

# Redis连接配置
REDIS_HOST = '192.168.3.242'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = 'redis123'
WS_URL = 'http://localhost:5057/socket.io'

def test_redis_connection():
    try:
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
        r.ping()
        print("✅ Redis连接成功")
        return r
    except Exception as e:
        print(f"❌ Redis连接失败: {e}")
        return None

def test_websocket_connection():
    try:
        sio = socketio.Client(engineio_logger=True, reconnection=False)
        
        @sio.event
        def connect():
            print("✅ WebSocket连接成功")
        
        @sio.event
        def connection_response(data):
            print(f"📩 收到连接响应: {data}")
        
        @sio.event
        def message_response(data):
            print(f"📩 收到消息响应: {data}")
        
        @sio.event
        def redis_data(data):
            print(f"📩 收到Redis数据: {data}")
        
        sio.connect(WS_URL)
        
        # 测试消息发送
        test_msg = {"text": "WebSocket测试消息"}
        sio.emit('message', test_msg)
        print(f"📤 发送测试消息: {test_msg}")
        
        # 测试Redis数据获取
        sio.emit('get_redis_data', {'key': 'corpus_input'})
        
        # 保持连接短暂时间
        time.sleep(2)
        sio.disconnect()
        return True
    except Exception as e:
        print(f"❌ WebSocket测试失败: {e}")
        return False

def test_save_data(r, test_key="test_inputs"):
    test_data = {"0": "测试数据1", "1": "测试数据2"}
    
    try:
        r.set(test_key, json.dumps(test_data))
        print(f"✅ 测试数据已保存到Redis (key: {test_key})")
        
        saved_data = r.get(test_key)
        if saved_data:
            print(f"📝 从Redis读取的数据: {json.loads(saved_data)}")
            return True
        return False
    except Exception as e:
        print(f"❌ 保存/读取测试数据失败: {e}")
        return False

def test_api_endpoint():
    test_url = f"{WS_URL}/api/test_redis"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    test_data = {"text": json.dumps({"test": "API测试数据"})}
    
    try:
        response = requests.post(test_url, headers=headers, data=json.dumps(test_data))
        print(f"🔄 API响应状态码: {response.status_code}")
        try:
            print(f"📄 API响应内容: {response.json()}")
        except:
            print(f"📄 API原始响应: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        return False

if __name__ == "__main__":
    print("\n=== 开始测试 ===")
    
    # 测试1: Redis连接
    r = test_redis_connection()
    if not r:
        exit(1)
    
    # 测试2: WebSocket连接
    print("\n--- 测试WebSocket连接 ---")
    if test_websocket_connection():
        print("✅ WebSocket测试通过")
    else:
        print("❌ WebSocket测试失败")
    
    # 测试3: 直接Redis操作
    print("\n--- 测试直接Redis操作 ---")
    if test_save_data(r):
        print("✅ 直接Redis操作测试通过")
    else:
        print("❌ 直接Redis操作测试失败")
    
    # 测试4: API端点测试
    print("\n--- 测试API端点 ---")
    if test_api_endpoint():
        print("✅ API端点测试通过")
    else:
        print("❌ API端点测试失败")
    
    print("\n=== 测试完成 ===")
