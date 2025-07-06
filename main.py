import threading
import subprocess
import time

def run_streamlit():
    print("Starting Streamlit App...")
    subprocess.run(["streamlit", "run", "temp.py"])

def run_voice_assistant():
    print("Starting Voice Assistant...")
    subprocess.run(["python", "vosk_stt.py"])

streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
voice_thread = threading.Thread(target=run_voice_assistant, daemon=True)

streamlit_thread.start()
voice_thread.start()


while True:
    time.sleep(1)
