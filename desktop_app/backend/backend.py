import threading
import subprocess
import sys
import webview
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('frontend/templates/HomePage.html')

def start_flask():
    app.run(host='127.0.0.1', port=5000)

def start_async_backend():
    subprocess.Popen([sys.executable, "jarvis_core.py"])

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    threading.Thread(target=start_async_backend, daemon=True).start()

    webview.create_window("Jarvis UI", "http://127.0.0.1:5000", fullscreen=True)
    webview.start()