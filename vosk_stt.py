import os
import queue
import json
import time
import threading
import pygame
import io
import schedule
import sounddevice as sd
import vosk
import requests
from gtts import gTTS
TELEGRAM_TOKEN = "7782069644:AAGS7JL4aY-1jvG9NLJlyf9btaRx40PBO60"
CHAT_ID = "1458744191"

MODEL_PATH = "vosk_model"
if not os.path.exists(MODEL_PATH):
    print("Model not found! Download and extract it first.")
    exit(1)

model = vosk.Model(MODEL_PATH)
samplerate = 16000
audio_queue = queue.Queue()

def speak(text):
    tts = gTTS(text=text, lang="en")
    
    speech_buffer = io.BytesIO()
    tts.write_to_fp(speech_buffer)
    speech_buffer.seek(0)
    
    pygame.mixer.init()
    pygame.mixer.music.load(speech_buffer, "mp3")
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(1)

def send_msg(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Message sent to Telegram")
    else:
        print(f"Failed to send Telegram message: {response.text}")
def medication_reminder():
    message = "It's time to take your medicine. Please take it now."
    print(f"[Reminder] {message}")
    speak(message)

def hydration_reminder():
    message = "Please drink some water to stay hydrated."
    print(f"[Reminder] {message}")
    speak(message)

def process_command(text):
    text = text.lower()

    if "help" in text or "sos" in text:
        print(" SOS Alert Detected! Sending message...")
        speak("Sending SOS alert...")
        send_msg("Warning!! The patient needs help")

def callback(indata, frames, time, status):
    if status:
        print(status)
    audio_queue.put(bytes(indata))

def run_voice_recognition():
    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype="int16",
                           channels=1, callback=callback):
        print(" Listening for voice commands...")
        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = audio_queue.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                recognized_text = result.get("text", "")
                if recognized_text:
                    print("You said:", recognized_text)
                    process_command(recognized_text)

schedule.every().day.at("09:00").do(medication_reminder)  # 9 AM
schedule.every().day.at("13:00").do(medication_reminder)  # 1 PM
schedule.every().day.at("21:00").do(medication_reminder)  # 9 PM
schedule.every(30).minutes.do(hydration_reminder)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1) 

scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
voice_thread = threading.Thread(target=run_voice_recognition, daemon=True)

scheduler_thread.start()
voice_thread.start()

print("Voice Assistant Running... Press Ctrl+C to stop.")
while True:
    time.sleep(1)
