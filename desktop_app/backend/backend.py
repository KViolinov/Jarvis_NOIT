# import threading
# import subprocess
# import sys
# import webview
# from flask import Flask, render_template

# app = Flask(__name__)

# @app.route('/')
# def index():
#     return render_template('Jarvis_NOIT/desktop_app/frontend/templates/HomePage.html')

# def start_flask():
#     app.run(host='127.0.0.1', port=5000)

# # def start_async_backend():
# #     subprocess.Popen([sys.executable, "jarvis_core.py"])

# if __name__ == '__main__':
#     threading.Thread(target=start_flask, daemon=True).start()
#     #threading.Thread(target=start_async_backend, daemon=True).start()

#     webview.create_window("Jarvis UI", "http://127.0.0.1:5000", fullscreen=True)
#     webview.start()


import os
import threading
import sys
import webview
from flask import Flask, render_template

# Absolute paths to template and static folders
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Home page
@app.route('/')
def index():
    return render_template('HomePage.html')

# Devices page
@app.route('/devices')
def devices():
    return render_template('DevicesPage.html')

# Settings page
@app.route('/settings')
def settings():
    return render_template('SettingsPage.html')

# Profile page
@app.route('/profile')
def profile():
    return render_template('ProfilePage.html')

# Login page
@app.route('/login')
def login():
    return render_template('Login.html')

# Sign-up page
@app.route('/signup')
def signup():
    return render_template('SignUp.html')

# Start Flask server in a separate thread
def start_flask():
    app.run(host='127.0.0.1', port=5000)

# Launch the desktop window
if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    webview.create_window("Jarvis UI", "http://127.0.0.1:5000", fullscreen=True)
    webview.start()
