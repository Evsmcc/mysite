from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'

# 获取环境变量中的端口，如果不存在则使用默认端口8080
port = int(os.environ.get('PORT', 8080))

# 初始化SocketIO - 配置为支持PythonAnywhere
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',  # 使用线程模式，兼容PythonAnywhere
    logger=True,
    engineio_logger=True
)

# 存储客户端连接
clients = set()


@socketio.on('connect')
def handle_connect():
    clients.add(request.sid)
    print(f'Client connected. Total clients: {len(clients)}')
    emit('status', {'msg': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    clients.discard(request.sid)
    print(f'Client disconnected. Total clients: {len(clients)}')


@socketio.on('message')
def handle_message(data):
    print(f'Received message: {data}')
    
    # 根据消息类型分发处理
    message_type = data.get('type')
    
    if message_type == 'boardState':
        # 处理棋盘状态更新
        socketio.emit('boardState', data.get('board', {}), include_self=True)
    elif message_type == 'chat':
        # 处理聊天消息
        socketio.emit('chat', data, include_self=True)
    elif message_type == 'move':
        # 处理棋子移动
        socketio.emit('move', data, include_self=True)
    else:
        # 处理其他类型的消息
        socketio.emit('message', data, include_self=True)


@socketio.on('chat')
def handle_chat(data):
    print(f'Received chat message: {data}')
    # 广播聊天消息给所有客户端
    socketio.emit('chat', data, include_self=True)


@socketio.on('move')
def handle_move(data):
    print(f'Received move message: {data}')
    # 广播棋步消息给所有客户端
    socketio.emit('move', data, include_self=True)


@socketio.on('boardState')
def handle_board_state(data):
    print(f'Received board state: {data}')
    # 广播棋盘状态给所有客户端
    socketio.emit('boardState', data, include_self=True)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    print(f'Starting Flask WebSocket server on port {port}')
    # 使用threading模式运行，兼容PythonAnywhere
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
