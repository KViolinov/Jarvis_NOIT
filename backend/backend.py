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

# import google.generativeai as genai

# from elevenlabs.client import ElevenLabs
# from elevenlabs import play
# from elevenlabs import voices  # ако искаш да видиш гласовете

# # --- Конфигурация за правилно показване на кирилица в конзолата ---
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# # --- API Keys and Configuration ---
# ELEVENLABS_API_KEY = "***"
# GEMINI_API_KEY = "***"

# # Създаване на ElevenLabs клиент с API ключа
# client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# genai.configure(api_key=GEMINI_API_KEY)
# GEMINI_MODEL = genai.GenerativeModel('gemini-1.5-flash')

# # Избор на глас (примерен ID, замени с твой)
# ELEVENLABS_VOICE_ID = "nPtk8Jc0J9F8K9X4Q9QW"

# r = sr.Recognizer()
# clients = set()

# current_state = "idle"
# state_lock = asyncio.Lock()

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

# conn = sqlite3.connect("iot_system.db")
# cursor = conn.cursor()

# # Добавяне в Devices (без DeviceID)
# cursor.execute("""
# DELETE FROM RGB WHERE LastColour = ? """, ("[128, 255, 64]",))

# conn.commit()
# conn.close()

# #print("Dobaveno ustroisto v RGB s ID:", device_id)
# print("ok")





import sqlite3

# Свързване към базата
conn = sqlite3.connect("jarvis_db.db")
cursor = conn.cursor()

# Извличане на списъка с таблици
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Преминаване през всяка таблица и извеждане на съдържанието ѝ
for table in tables:
    table_name = table[0]
    print(f"\ntable: {table_name}")
    print("-" * (10 + len(table_name)))

    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Извличане на имената на колоните
        col_names = [description[0] for description in cursor.description]
        print(" | ".join(col_names))
        print("-" * 50)

        if not rows:
            print("[nqma zapisi]")
        else:
            for row in rows:
                print(" | ".join(str(x) for x in row))

    except Exception as e:
        print("⚠️ Error in reading the DB:", e)

# Затваряне
conn.close()


