# import asyncio
# import websockets
# import json
# import speech_recognition as sr
# import sys
# import io
# import threading

# # --- Конфигурация за правилно показване на кирилица в конзолата ---
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# # --- Инициализация на разпознаването на реч ---
# r = sr.Recognizer()
# clients = set()

# def record_text():
#     """
#     Слуша за аудио от микрофона и го превръща в текст.
#     Тази функция е БЛОКИРАЩА.
#     """
#     try:
#         with sr.Microphone() as source:
#             r.adjust_for_ambient_noise(source, duration=0.2)
#             print("Слушам за команда...")
#             audio = r.listen(source)
#             MyText = r.recognize_google(audio, language="bg-BG")
#             print(f"Вие казахте: {MyText}")
#             return MyText.lower()
#     except sr.RequestError as e:
#         print(f"Грешка в заявката към API-то; {e}")
#         return None
#     except sr.UnknownValueError:
#         print("Не можах да разбера казаното. Моля, опитайте отново.")
#         return None
#     except Exception as e:
#         print(f"Възникна неочаквана грешка: {e}")
#         return None

# async def send_to_all(message):
#     """Изпраща съобщение до всички свързани клиенти."""
#     if clients:
#         await asyncio.gather(*[client.send(message) for client in clients])

# async def recognize_loop():
#     """
#     Основен цикъл, който постоянно слуша за ключовата дума.
#     """
#     loop = asyncio.get_running_loop()
#     while True:
#         # Извикваме блокиращата функция в отделна нишка (thread)
#         text = await loop.run_in_executor(None, record_text)
        
#         if text and "джарвис" in text:
#             print("🟢 Ключовата дума 'Джарвис' е разпозната!")
#             msg = json.dumps({"wake_word": "Jarvis"})
#             # Използваме call_soon_threadsafe, за да изпратим съобщението
#             # от нишката към основния asyncio цикъл.
#             asyncio.run_coroutine_threadsafe(send_to_all(msg), loop)

# # --- КЛЮЧОВА ПРОМЯНА ---
# # Връщаме сигнатурата на функцията към оригиналния й вид с един аргумент,
# # за да е съвместима с твоята версия на библиотеката websockets.
# async def handler(websocket):
#     """
#     Обработва нови WebSocket връзки.
#     """
#     print(f"✅ Клиент се свърза от {websocket.remote_address}")
#     clients.add(websocket)
#     try:
#         await websocket.wait_closed()
#     finally:
#         print(f"❌ Клиент {websocket.remote_address} се разкачи.")
#         clients.remove(websocket)

# async def main():
#     """
#     Главна асинхронна функция, която стартира сървъра и цикъла за разпознаване.
#     """
#     # Стартираме цикъла за разпознаване в отделна нишка
#     threading.Thread(target=lambda: asyncio.run(recognize_loop()), daemon=True).start()
    
#     print("🚀 Стартиране на WebSocket сървъра на ws://localhost:8765 ...")
#     async with websockets.serve(handler, "localhost", 8765):
#         await asyncio.Future()  # Работи вечно

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("\nСървърът е спрян.")





# import asyncio
# import websockets
# import json
# import speech_recognition as sr
# import sys
# import io
# import threading
# import os
# import sqlite3
# from dotenv import load_dotenv

# import google.generativeai as genai

# from elevenlabs.client import ElevenLabs
# from elevenlabs import play
# from elevenlabs import voices  # ако искаш да видиш гласовете

# import serial
# import time

# PORT = 'COM4'       # Смени с твоя сериен порт
# BAUD_RATE = 115200

# # --- Конфигурация за правилно показване на кирилица в конзолата ---
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# # --- API Keys and Configuration ---
# ELEVENLABS_API_KEY = os.getenv("ELEVEN_LABS_API")
# GEMINI_API_KEY = os.getenv("GEMINI_KEY")

# # Създаване на ElevenLabs клиент с API ключа
# client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# genai.configure(api_key=GEMINI_API_KEY)
# GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')

# # Избор на глас (примерен ID, замени с твой)
# ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

# r = sr.Recognizer()
# clients = set()

# current_state = "idle"
# state_lock = asyncio.Lock()

# load_dotenv()

# async def set_state(new_state: str):
#     global current_state
#     async with state_lock:
#         if current_state != new_state:
#             print(f"Changing state from '{current_state}' to '{new_state}'")
#             current_state = new_state
#             message = json.dumps({"state": current_state})
#             await send_to_all(message)

# def record_text_blocking():
#     try:
#         with sr.Microphone() as source:
#             r.adjust_for_ambient_noise(source, duration=0.2)
#             print(f"[{current_state}] Слушам за команда...")
#             audio = r.listen(source)
#             MyText = r.recognize_google(audio, language="bg-BG")
#             print(f"[{current_state}] Вие казахте: {MyText}")
#             return MyText.lower()
#     except sr.RequestError as e:
#         print(f"[{current_state}] Грешка в заявката към API-то; {e}")
#         return None
#     except sr.UnknownValueError:
#         print(f"[{current_state}] Не разбрах казаното.")
#         return None
#     except Exception as e:
#         print(f"[{current_state}] Неочаквана грешка: {e}")
#         return None

# async def synthesize_speech(text: str):
#     print(f"[{current_state}] Синтезирам реч с Eleven Labs: '{text}'...")
#     try:
#         audio = client.generate(text=text, voice=ELEVENLABS_VOICE_ID)
#         play(audio)
#         print(f"[{current_state}] Аудиото е възпроизведено.")
#     except Exception as e:
#         print(f"[{current_state}] Грешка при синтез и възпроизвеждане: {e}")

# async def get_gemini_response(prompt: str) -> str:
#     print(f"[{current_state}] Изпращам промпт към Gemini: '{prompt}'...")
#     try:
#         response = GEMINI_MODEL.generate_content(prompt)
#         if hasattr(response, 'text') and response.text:
#             print(f"[{current_state}] Отговор от Gemini: {response.text}")
#             return response.text
#         else:
#             print(f"[{current_state}] Gemini не върна текст.")
#             return "Съжалявам, не мога да отговоря."
#     except Exception as e:
#         print(f"[{current_state}] Грешка при Gemini API: {e}")
#         return "Грешка при свързване с Gemini."

# async def send_to_all(message):
#     if clients:
#         await asyncio.gather(*[client.send(message) for client in clients])

# async def recognize_loop():
#     loop = asyncio.get_running_loop()
#     while True:
#         await set_state("idle")
#         print("Слушам за 'Джарвис'...")
#         text = await loop.run_in_executor(None, record_text_blocking)
#         if text and "джарвис" in text or "джарви" in text:
#             print("🟢 'Джарвис' е разпознат!")
#             await set_state("listening")
#             await synthesize_speech("Слушам")
#             user_command = await loop.run_in_executor(None, record_text_blocking)
#             if user_command:
#                 print(f"❓ Потребителят каза: {user_command}")
#                 await set_state("answering")
#                 gemini_answer = await get_gemini_response(user_command)
#                 if gemini_answer:
#                     await synthesize_speech(gemini_answer)
#             else:
#                 print("⚠️ Не разбрах командата след 'Джарвис'.")
#         else:
#             await asyncio.sleep(0.5)

# async def handler(websocket):
#     print(f"✅ Клиент се свърза: {websocket.remote_address}")
#     clients.add(websocket)
#     await websocket.send(json.dumps({"state": current_state}))
#     try:
#         await websocket.wait_closed()
#     finally:
#         print(f"❌ Клиент се разкачи: {websocket.remote_address}")
#         clients.remove(websocket)

# async def sendToDevice(message:str, macAddress:str):
#     try:
#         ser = serial.Serial(PORT, BAUD_RATE, timeout=5)
#         time.sleep(2)  # Изчаква ESP-то да стартира
#         print(f"Connected to the {PORT}")
#     except serial.SerialException as e:
#         print("Error in opening the serial port:", e)
#         exit(1)

#     if message == "get":
#         # Изпращаме командата "get"
#         ser.write(f'get {macAddress}\n'.encode())
#         print("🔁 Sent: get")

#         # Четем отговора на ESP-то
#         while True:
#             if ser.in_waiting > 0:
#                 line = ser.readline().decode('utf-8', errors='ignore').strip()
#                 if line:
#                     print("📥 Received:", line)
#                     # Спиране, ако сме получили очаквания отговор
#                     if "Temperature:" in line or "Humidity:" in line:
#                         break


#     elif message == "get2":
#         # Изпращаме командата "get"
#         ser.write(f'get2 {macAddress}\n'.encode())
#         print("🔁 Sent: get2")

#         # Четем отговора на ESP-то
#         while True:
#             if ser.in_waiting > 0:
#                 line = ser.readline().decode('utf-8', errors='ignore').strip()
#                 if line:
#                     print("📥 Received:", line)
#                     # Спиране, ако сме получили очаквания отговор
#                     if "Temperature:" in line or "Humidity:" in line:
#                         break

#     ser.close()
#     print("Connection is ended.")

# async def checkDBforActivity():
#     # Свързване към базата
#     conn = sqlite3.connect("jarvis_db.db")
#     cursor = conn.cursor()

#     print("table: Relay")
#     print("-" * 20)

#     try:
#         # Заявка само за Relay: Checked == 0 и FIFO по TimeOfRecord
#         cursor.execute("""
#             SELECT * FROM Relay
#             WHERE Checked = 0
#             ORDER BY TimeOfRecord ASC
#         """)

#         rows = cursor.fetchall()

#         # Имена на колоните
#         col_names = [description[0] for description in cursor.description]
#         print(" | ".join(col_names))
#         print("-" * 50)

#         if not rows:
#             print("[nqma zapisi]")
#         else:
#             for row in rows:
#                 print(" | ".join(str(x) for x in row))

#     except Exception as e:
#         print("⚠️ Error in reading Relay:", e)

#     # Затваряне
#     conn.close()


# async def main():
#     threading.Thread(target=lambda: asyncio.run(recognize_loop()), daemon=True).start()
#     print("🚀 Стартирам WebSocket сървър на ws://localhost:8765 ...")
#     async with websockets.serve(handler, "localhost", 8765):
#         await asyncio.Future()

# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("\nСървърът е спрян.")






# import sqlite3

# # Свързване към базата
# conn = sqlite3.connect("jarvis_db.db")
# cursor = conn.cursor()

# # Извличане на списъка с таблици
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()

# # Преминаване през всяка таблица и извеждане на съдържанието ѝ
# for table in tables:
#     table_name = table[0]
#     print(f"\ntable: {table_name}")
#     print("-" * (10 + len(table_name)))

#     try:
#         cursor.execute(f"SELECT * FROM {table_name}")
#         rows = cursor.fetchall()

#         # Извличане на имената на колоните
#         col_names = [description[0] for description in cursor.description]
#         print(" | ".join(col_names))
#         print("-" * 50)

#         if not rows:
#             print("[nqma zapisi]")
#         else:
#             for row in rows:
#                 print(" | ".join(str(x) for x in row))

#     except Exception as e:
#         print("⚠️ Error in reading the DB:", e)

# # Затваряне
# conn.close()




import asyncio
import websockets
import json
import speech_recognition as sr
import sys
import io
import threading
import os
import sqlite3
import urllib
from dotenv import load_dotenv

import google.generativeai as genai
from ollama import chat
from ollama import ChatResponse

from elevenlabs.client import ElevenLabs
from elevenlabs import play
from elevenlabs import voices

import serial
import time
from datetime import datetime

PORT = 'COM4'
BAUD_RATE = 115200

# --- Конфигурация за кирилица ---
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVEN_LABS_API")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID")

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

genai.configure(api_key=GEMINI_API_KEY)
GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')

r = sr.Recognizer()
clients = set()

current_state = "idle"
state_lock = asyncio.Lock()

async def set_state(new_state: str):
    global current_state
    async with state_lock:
        if current_state != new_state:
            print(f"Changing state from '{current_state}' to '{new_state}'")
            current_state = new_state
            message = json.dumps({"state": current_state})
            await send_to_all(message)

def record_text_blocking():
    try:
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            print(f"[{current_state}] Слушам за команда...")
            audio = r.listen(source)
            MyText = r.recognize_google(audio, language="bg-BG")
            print(f"[{current_state}] Вие казахте: {MyText}")
            return MyText.lower()
    except sr.RequestError as e:
        print(f"[{current_state}] Грешка в заявката към API-то; {e}")
        return None
    except sr.UnknownValueError:
        print(f"[{current_state}] Не разбрах казаното.")
        return None
    except Exception as e:
        print(f"[{current_state}] Неочаквана грешка: {e}")
        return None

async def synthesize_speech(text: str):
    print(f"[{current_state}] Синтезирам реч с Eleven Labs: '{text}'...")
    try:
        audio = client.generate(text=text, voice=ELEVENLABS_VOICE_ID)
        play(audio)
        print(f"[{current_state}] Аудиото е възпроизведено.")
    except Exception as e:
        print(f"[{current_state}] Грешка при синтез и възпроизвеждане: {e}")

async def get_gemini_response(prompt: str) -> str:
    print(f"[{current_state}] Изпращам промпт към Gemini: '{prompt}'...")
    try:
        response = GEMINI_MODEL.generate_content(prompt)
        if hasattr(response, 'text') and response.text:
            print(f"[{current_state}] Отговор от Gemini: {response.text}")
            return response.text
        else:
            print(f"[{current_state}] Gemini не върна текст.")
            return "Съжалявам, не мога да отговоря."
    except Exception as e:
        print(f"[{current_state}] Грешка при Gemini API: {e}")
        return "Грешка при свързване с Gemini."

async def get_tiny_llama_response(prompt:str ) -> str:
    print(f"[{current_state}] Изпращам промпт към Локалния модел (tiny llama): '{prompt}'...")
    
    response: ChatResponse = chat(model='gemma3', messages=[
    {
        'role': 'user',
        'content': {prompt},
    },
    ])

    print(response['message']['content'])
    print(response.message.content)
    return response.message.content

async def send_to_all(message):
    if clients:
        await asyncio.gather(*[client.send(message) for client in clients])

async def recognize_loop():
    loop = asyncio.get_running_loop()
    while True:
        await set_state("idle")
        print("Слушам за 'Джарвис'...")
        text = await loop.run_in_executor(None, record_text_blocking)
        
        if text and ("джарвис" in text or "джарви" in text):
            print("🟢 'Джарвис' е разпознат!")
            await set_state("listening")
            await synthesize_speech("Слушам")
            user_command = await loop.run_in_executor(None, record_text_blocking)
            
            if user_command:
                print(f"❓ Потребителят каза: {user_command}")
                await set_state("answering")
                if(checkWifi()):
                    model_answer = await get_gemini_response(user_command)
                else:
                    model_answer = await get_tiny_llama_response(user_command)

                if model_answer:
                    await synthesize_speech(model_answer)
            else:
                print("⚠️ Не разбрах командата след 'Джарвис'.")
        else:
            await asyncio.sleep(0.5)

async def handler(websocket):
    print(f"✅ Клиент се свърза: {websocket.remote_address}")
    clients.add(websocket)
    await websocket.send(json.dumps({"state": current_state}))
    try:
        await websocket.wait_closed()
    finally:
        print(f"❌ Клиент се разкачи: {websocket.remote_address}")
        clients.remove(websocket)

def sendInitToDevice(macAddress: str) -> bool:
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=5)
        time.sleep(2)  # Изчаква ESP-то да стартира
        print(f"Connected to the {PORT}")
    except serial.SerialException as e:
        print("Error in opening the serial port:", e)
        return ""  # Return empty string on error

    ser.write(f'init {macAddress}\n'.encode())
    print(f"🔁 Sent: init to {macAddress}")

    line = ""
    start_time = time.time()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line == "Connection Successful":
                print("📥 Received:", line)
                break
        # Optional: timeout after 5 seconds
        if time.time() - start_time > 5:
            print("⚠️ Timeout waiting for response.")
            break

    ser.close()
    print("Connection is ended.")
    return True

def sendGetToDevice(macAddress: str) -> str:
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=5)
        time.sleep(2)  # Изчаква ESP-то да стартира
        print(f"Connected to the {PORT}")
    except serial.SerialException as e:
        print("Error in opening the serial port:", e)
        return ""  # Return empty string on error

    ser.write(f'get {macAddress}\n'.encode())
    print("🔁 Sent: get")

    line = ""
    start_time = time.time()
    while True:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print("📥 Received:", line)
                break
        # Optional: timeout after 5 seconds
        if time.time() - start_time > 5:
            print("⚠️ Timeout waiting for response.")
            break

    ser.close()
    print("Connection is ended.")
    return line

def sendGetToDevice(macAddress:str, message:str, deviceType:str) -> str:
    try:
        ser = serial.Serial(PORT, BAUD_RATE, timeout=5)
        time.sleep(2)  # Изчаква ESP-то да стартира
        print(f"Connected to the {PORT}")
    except serial.SerialException as e:
        print("Error in opening the serial port:", e)
        exit(1)

    if(deviceType == "IR"):
        # Изпращаме командата "get2"
        ser.write(f'get2 {macAddress} {message}\n'.encode())
        print("🔁 Sent: get2")

        # Четем отговора на ESP-то
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print("📥 Received:", line)
                    break
                
    elif(deviceType == "RGB"):
        # Изпращаме командата "get2"
        messageToSend = message + " - " + "[Red;Green;Blue;Intensity]"

        ser.write(f'get2 {macAddress} {messageToSend}\n'.encode())
        print("🔁 Sent: get2")

        # Четем отговора на ESP-то
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print("📥 Received:", line)
                    break

    ser.close()
    print("Connection is ended.")
    return line

async def checkDHTSensor():
    macAddress = searchMacAddressInDB("DHT")
    data = sendGetToDevice(macAddress)

    temperature = None
    humidity = None

        # Example data: "T:23.5f,H:22.0f"
    try:
        parts = data.split(',')
        for part in parts:
            if part.startswith("T:"):
                temperature = part.split(":")[1].replace("f", "").strip()
            elif part.startswith("H:"):
                humidity = part.split(":")[1].replace("f", "").strip()
    except Exception as e:
        print("Error parsing DHT data:", e)

    # Insert into DHT table
    conn = sqlite3.connect("jarvis_db.db")
    cursor = conn.cursor()

    time_of_record = getTime()
    
    cursor.execute("""
        INSERT INTO DHT (DeviceMACID, LastTemperature, LastHumidity, TimeOfRecord)
        VALUES (?, ?, ?, ?)
    """, (macAddress, temperature, humidity, time_of_record))

    conn.commit()
    conn.close()

async def checkDBforActivity():
    """Проверява базата без да блокира event loop."""
    def query_db():
        # Searching for activity in table Relay
        conn = sqlite3.connect("jarvis_db.db")
        conn.row_factory = sqlite3.Row  # This allows access by column name
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM Relay
            WHERE Checked = 0
            ORDER BY TimeOfRecord ASC
        """)
        rows = cursor.fetchall()

        if not rows:
            print("[nqma zapisi]")  # No records found
        else:
            for row in rows:
                device_mac = row["DeviceMACID"]
                last_state = row["LastState"]
                time_of_record = row["TimeOfRecord"]
                checked = row["Checked"]
                print(f"MAC: {device_mac}, State: {last_state}, Time: {time_of_record}, Checked: {checked}")

                sendGetToDevice(macAddress=device_mac)

                # Delete the current row
                cursor.execute("""
                    DELETE FROM Relay
                    WHERE DeviceMACID = ? AND TimeOfRecord = ?
                """, (device_mac, time_of_record))

                print(f"Deleted row with MAC: {device_mac} and Time: {time_of_record}")

        conn.commit()

        # Searching for activity in table RGB
        conn = sqlite3.connect("jarvis_db.db")
        conn.row_factory = sqlite3.Row  # This allows access by column name
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM RGB
            WHERE Checked = 0
            ORDER BY TimeOfRecord ASC
        """)
        rows = cursor.fetchall()

        if not rows:
            print("[nqma zapisi]")  # No records found
        else:
            for row in rows:
                device_mac = row["DeviceMACID"]
                last_colour = row["LastColour"]
                last_intensity = row["LastIntensity"]
                time_of_record = row["TimeOfRecord"]
                checked = row["Checked"]
                print(f"MAC: {device_mac}, State: {last_colour}, Type: {last_intensity}, Time: {time_of_record}, Checked: {checked}")

                messageToSend = last_colour + " " + last_intensity
                sendGetToDevice(macAddress=device_mac, message=messageToSend)

                # Delete the current row
                cursor.execute("""
                    DELETE FROM RGB
                    WHERE DeviceMACID = ? AND TimeOfRecord = ?
                """, (device_mac, time_of_record))

                print(f"Deleted row with MAC: {device_mac} and Time: {time_of_record}")

        conn.commit()


        # Searching for activity in table IR
        conn = sqlite3.connect("jarvis_db.db")
        conn.row_factory = sqlite3.Row  # This allows access by column name
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM IR
            WHERE Checked = 0
            ORDER BY TimeOfRecord ASC
        """)
        rows = cursor.fetchall()

        if not rows:
            print("[nqma zapisi]")  # No records found
        else:
            for row in rows:
                device_mac = row["DeviceMACID"]
                last_code_sent = row["LastCodeSent"]
                time_of_record = row["TimeOfRecord"]
                checked = row["Checked"]
                print(f"MAC: {device_mac}, State: {last_state}, Code: {last_code_sent}, Time: {time_of_record}, Checked: {checked}")

                sendGetToDevice(macAddress=device_mac, message=last_code_sent)

                # Delete the current row
                cursor.execute("""
                    DELETE FROM IR
                    WHERE DeviceMACID = ? AND TimeOfRecord = ?
                """, (device_mac, time_of_record))

                print(f"Deleted row with MAC: {device_mac} and Time: {time_of_record}")

        conn.commit()


    await asyncio.to_thread(query_db)

async def db_loop():
    """Изпълнява checkDBforActivity() на всеки 5 секунди."""
    while True:
        await checkDBforActivity()
        await asyncio.sleep(5)

async def dht_loop():
    """Изпълнява checkDHTSensor() на всеки 15 минути."""
    while True:
        await checkDHTSensor()
        await asyncio.sleep(900)

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

def searchMacAddressInDB(deviceType: str) -> str: # not sure if it works
    conn = sqlite3.connect("jarvis_db.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DeviceMACID FROM Devices
        WHERE DeviceType = ?
    """, (deviceType,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else ""

async def main():
    # Стартираме voice loop в отделен thread
    threading.Thread(target=lambda: asyncio.run(recognize_loop()), daemon=True).start()
    # Стартираме DB loop в asyncio
    asyncio.create_task(db_loop())
    asyncio.create_task(dht_loop())

    print("🚀 Стартирам WebSocket сървър на ws://localhost:8765 ...")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nСървърът е спрян.")
