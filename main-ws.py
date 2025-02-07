from flask import Flask
from flask_socketio import SocketIO
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app)

def background_thread():
    while True:
        time.sleep(5)  # Update every 5 seconds
        socketio.emit('update', {'data': 'New data'})

@app.route('/')
def index():
    return "WebSocket Server"

if __name__ == '__main__':
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()
    socketio.run(app, port=5000)