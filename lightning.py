from app import socketio
from app import app
import os

port = int(os.environ.get('PORT', 5000))
if __name__ == '__main__':
    socketio.run(app, port=port, host='0.0.0.0')
