from core import create_app
import os

app, socketio = create_app()

if __name__ == "__main__":    
    socketio.run(app, debug=True, port=8000)