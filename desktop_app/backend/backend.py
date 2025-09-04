# # import os
# # import threading
# # import sys
# # import webview
# # from flask import Flask, render_template

# # # Absolute paths to template and static folders
# # template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'))
# # static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))

# # app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# # # Home page
# # @app.route('/')
# # def index():
# #     return render_template('HomePage.html')

# # # Devices page
# # @app.route('/devices')
# # def devices():
# #     return render_template('DevicesPage.html')

# # # Settings page
# # @app.route('/settings')
# # def settings():
# #     return render_template('SettingsPage.html')

# # # Profile page
# # @app.route('/profile')
# # def profile():
# #     return render_template('ProfilePage.html')

# # # Login page
# # @app.route('/login')
# # def login():
# #     return render_template('Login.html')

# # # Sign-up page
# # @app.route('/signup')
# # def signup():
# #     return render_template('SignUp.html')

# # # Start Flask server in a separate thread
# # def start_flask():
# #     app.run(host='127.0.0.1', port=5000)

# # # Launch the desktop window
# # if __name__ == '__main__':
# #     threading.Thread(target=start_flask, daemon=True).start()
# #     webview.create_window("Jarvis UI", "http://127.0.0.1:5000", fullscreen=True)
# #     webview.start()



# # import os
# # import threading
# # import webview
# # from flask import Flask, render_template
# # from jarvis_core import start_jarvis_core  # import your core logic

# # # Absolute paths to template and static folders
# # template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'))
# # static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))

# # app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# # # ---------------- Flask routes ---------------- #
# # @app.route('/')
# # def index():
# #     return render_template('HomePage.html')

# # @app.route('/devices')
# # def devices():
# #     return render_template('DevicesPage.html')

# # @app.route('/settings')
# # def settings():
# #     return render_template('SettingsPage.html')

# # @app.route('/profile')
# # def profile():
# #     return render_template('ProfilePage.html')

# # @app.route('/login')
# # def login():
# #     return render_template('Login.html')

# # @app.route('/signup')
# # def signup():
# #     return render_template('SignUp.html')

# # # ---------------- Background runners ---------------- #
# # def start_flask():
# #     app.run(host='127.0.0.1', port=5000)

# # def run_jarvis_core():
# #     import asyncio
# #     from jarvis_core import start_jarvis_core
# #     asyncio.run(start_jarvis_core())

# # if __name__ == '__main__':
# #     flask_thread = threading.Thread(target=start_flask, daemon=True)
# #     flask_thread.start()

# #     # FIX: Use run_jarvis_core instead of start_jarvis_core directly
# #     jarvis_thread = threading.Thread(target=run_jarvis_core, daemon=True)
# #     jarvis_thread.start()

# #     webview.create_window("Jarvis UI", "http://127.0.0.1:5000")
# #     webview.start()


import os
import threading
import asyncio
import json
import queue
import sys
import io

import speech_recognition as sr
import websockets
import webview

from flask import Flask, render_template, request, jsonify
import logging

from dotenv import load_dotenv

from elevenlabs.client import ElevenLabs
from elevenlabs import play
from gtts import gTTS
from io import BytesIO

import google.generativeai as genai
import ollama

import argostranslate.package
import argostranslate.translate

from pathlib import Path

from pydub import AudioSegment
import pyaudio

import random
import datetime
import urllib.request


load_dotenv()

# --- Force UTF-8 output ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sound_path = os.path.join(BASE_DIR, "beep.flac")

ELEVENLABS_API_KEY = os.getenv("ELEVEN_LABS_API")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
genai.configure(api_key=GEMINI_API_KEY)

GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')
system_prompt = """Ти си Джарвис, личният AI асистент на Константин. Характеристики:
    
    ЛИЧНОСТ:
    - Говориш само на български език
    - Отговаряш кратко и директно (максимум 2-3 изречения)
    - Си професионален, но приятелски настроен
    - Винаги си готов да помогнеш
    - Имаш чувство за хумор, но не прекаляваш
    
    ВЪЗМОЖНОСТИ:
    - Управляваш умен дом (осветление, температура, устройства)
    - Отговаряш на въпроси за всичко
    - Помагаш с планиране и напомняния
    - Водиш естествени разговори
    - Предоставяш информация за времето, новини, факти
    
    ПРАВИЛА:
    - Винаги отговаряй на български
    - Бъди кратък и точен
    - Ако не знаеш нещо, кажи честно
    - При управление на устройства, потвърди действието
    - Обръщай се към потребителя като "Константин" или просто отговаряй директно"""

jarvis_responses = [
    "Тук съм, как мога да помогна?",
    "Слушам, как мога да Ви асистирам?",
    "Тук съм, как мога да помогна?",
    "С какво мога да Ви бъда полезен?"
    #"Слушам шефе, как да помогна?"
]

# --- Flask setup ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_dir = os.path.join(BASE_DIR, 'frontend', 'templates')
static_dir = os.path.join(BASE_DIR, 'frontend', 'static')

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

# Disable Flask/Werkzeug logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def index():
    return render_template('HomePage.html')

@app.route('/devices')
def devices():
    return render_template('DevicesPage.html')

@app.route('/settings')
def settings():
    return render_template('SettingsPage.html')

@app.route('/profile')
def profile():
    return render_template('ProfilePage.html')

@app.route('/login')
def login():
    return render_template('Login.html')

@app.route('/signup')
def signup():
    return render_template('SignUp.html')

@app.route('/toggle-light', methods=['POST'])
def toggle_light():
    data = request.get_json()
    light_id = data.get("id")
    state = data.get("state")
    print(f"[Backend] Light '{light_id}' set to {'ON' if state else 'OFF'}", flush=True)
    message_queue.put({"light": light_id, "state": state})
    return jsonify({"status": "ok", "light": light_id, "state": state})

def start_flask():
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)



# --- Jarvis Core ---
r = sr.Recognizer()
clients = set()
message_queue = queue.Queue()
current_state = "idle"

def play_flac_file(file_path):
    """Synchronous function to play a FLAC file using pydub and pyaudio."""
    # Load the FLAC file
    audio = AudioSegment.from_file(file_path, format="flac")

    # Setup PyAudio
    p = pyaudio.PyAudio()
    stream = p.open(
        format=p.get_format_from_width(audio.sample_width),
        channels=audio.channels,
        rate=audio.frame_rate,
        output=True
    )

    # Play the audio
    data = audio.raw_data
    stream.write(data)

    # Cleanup
    stream.stop_stream()
    stream.close()
    p.terminate()

async def set_state(state: str):
    global current_state
    current_state = state
    print(f"[STATE] Jarvis state changed to: {state}", flush=True)
    
    # Send state change to all WebSocket clients
    state_message = json.dumps({"type": "state_change", "state": state})
    await send_to_all(state_message)

def record_text_blocking():
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            print("🎤 Listening for command...", flush=True)
            audio = r.listen(source)
            MyText = r.recognize_google(audio, language="bg-BG")
            print(f"🗣️ You said: {MyText}", flush=True)
            return MyText.lower()
    except sr.RequestError as e:
        print(f"⚠️ API Error: {e}", flush=True)
        return None
    except sr.UnknownValueError:
        print("❌ Could not understand audio.", flush=True)
        return None
    except Exception as e:
        print(f"‼️ Error: {e}", flush=True)
        return None

async def send_to_all(message):
    if clients:
        await asyncio.gather(*[client.send(message) for client in clients])

async def get_gemini_response(prompt: str) -> str: # TODO - Need to add the system prompt
    print(f"[{current_state}] Sending prompt to Gemini: '{prompt}'...", flush=True)
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            print(f"[{current_state}] Gemini response: {response.text}", flush=True)
            return response.text
        else:
            return "Sorry, I cannot respond."
    except Exception as e:
        print(f"[{current_state}] Gemini API error: {e}", flush=True)
        return "Error connecting to Gemini."

async def get_tiny_llama_response(prompt:str ) -> str: # TODO not sure if this works, needs testing
    print(f"[{current_state}] Изпращам промпт към Локалния модел (tiny llama): '{prompt}'...")
    
    response: ChatResponse = chat(model='tinyllama', messages=[
    {
        'role': 'user',
        'content': {prompt},
    },
    ])

    print(response['message']['content'])

    # Translate
    translatedText = argostranslate.translate.translate(response['message']['content'], "en", "bg")

    print(translatedText)
    return translatedText

async def synthesize_speech(text: str): 
    audio = client.text_to_speech.convert(
    text=text,
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    model_id="eleven_multilingual_v2",
    output_format="mp3_44100_128",
)
    play(audio)

async def synthesize_speech_offline(text: str):
    # Generate TTS in memory
    tts = gTTS(text=text, lang='bg')
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)

    # Load and play audio
    audio = AudioSegment.from_file(fp, format="mp3")
    play(audio)

async def recognize_loop():
    loop = asyncio.get_running_loop()
    while True:
        await set_state("idle")
        print("🎧 Listening for 'Джарвис'...", flush=True)
        text = await loop.run_in_executor(None, record_text_blocking)

        if text and any(phrase in text for phrase in ("Джарвис", "джарвис", "джарви", "Jarvis", "jarvis", "джервис")):

            await asyncio.to_thread(play_flac_file, "D:\\Jarvis_NOIT\\desktop_app\\backend\\additional_things\\beep.flac")

            await set_state("listening")

            # await synthesize_speech(random.choice(jarvis_responses)) # TODO - works just online

            if checkWifi():
                await synthesize_speech(random.choice(jarvis_responses))
            else:
                await synthesize_speech_offline(random.choice(jarvis_responses))

            print("I am listening...", flush=True)

            user_input = await loop.run_in_executor(None, record_text_blocking)

            if not user_input:
                print("⚠️ Could not understand command after 'Джарвис'", flush=True)

            if any(phrase in user_input for phrase in ("представи се", "представиш", "представи")):
                synthesize_speech("Здравейте, аз съм Джарвис, акроним от (Just A Rather Very Intelligent System), аз съм езиков модел на Gemini обучен от Google."
                                    "Вдъхновен съм от легендарния изкуствен интелект на Тони Старк – Джарвис от Железния човек."
                                    "Моята мисия е да ви помогна с работата и управлението на вашия умен дом."
                                    "Ако искате да ме попитате нещо, просто ме повикайте по име.")
                continue

            if any(phrase in user_input for phrase in ("ново", "устройство", "свържа", "теб")):
                await synthesize_speech(
                "Супер, имаш ново устройсто. Сега ще ти кажа как можеш лесно да го свържеш към Jarvis Hub-a. " \
                "Просто отиди в страницата настройки и цъкни бутона \"Добави устройство\", " \
                "след като си отворил новата страница просто въведи специалния Mac адрес на новото ти устройство, " \
                "и като ти изпише на екрана \"Успех\", значи си го свързал правилно."
                "Ако има някакви проблеми с свързването, просто ми кажи.")
                continue

            if any(phrase in user_input for phrase in ("какво", "можеш", "правиш")):
                await synthesize_speech("Мога да търся информация в интернет, да я обобщавам и да ви я представям. "
                                             "Също така, мога да изпращам и чета имейли, да пускам музика, да отварям нови документи в Word "
                                             "И дори да ви опиша това, което виждам като изпозлвам Gemini Vision и OCR модел за разпознаване на текст")
                continue

            if user_input:
                print(f"❓ User said: {user_input}", flush=True)
                model_answer = await get_gemini_response(user_input)
                if model_answer:
                    await set_state("answering")
                    #await synthesize_speech(model_answer) # TODO - works just online
                    if checkWifi():
                        await synthesize_speech(model_answer)
                    else:
                        await synthesize_speech_offline(model_answer)
        else:
            await asyncio.sleep(0.5)

async def handler(websocket):
    print(f"✅ Client connected: {websocket.remote_address}", flush=True)
    clients.add(websocket)
    try:
        while True:
            # Handle light control messages from Flask
            if not message_queue.empty():
                command = message_queue.get()
                msg = json.dumps({"type": "light_control", **command})
                await websocket.send(msg)
                print(f"[Jarvis] Sent light command: {msg}", flush=True)
            await asyncio.sleep(0.1)
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        clients.remove(websocket)
        print(f"❌ Client disconnected: {websocket.remote_address}", flush=True)

def checkWifi() -> bool:
    try:
        url = "https://www.google.com"
        urllib.request.urlopen(url, timeout=5)
        return True
    except:
        return False

def getTime() -> str:
    current_time = datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    return current_state


async def jarvis_core():
    print("🚀 Jarvis WebSocket started at ws://localhost:8765", flush=True)
    asyncio.create_task(recognize_loop())
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

def start_jarvis():
    asyncio.run(jarvis_core())

# --- Main Entry ---
if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    threading.Thread(target=start_jarvis, daemon=True).start()
    webview.create_window("Jarvis UI", "http://127.0.0.1:5000", fullscreen=False)
    webview.start()