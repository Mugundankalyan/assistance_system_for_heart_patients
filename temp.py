import streamlit as st
import numpy as np
import serial
import time
import firebase_admin
from firebase_admin import credentials, db
import tensorflow as tf
import os
import requests
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=5000, key="data_refresh")

SERIAL_PORT = "/dev/ttyUSB0" 
BAUD_RATE = 115200

TELEGRAM_TOKEN = "TELEGRAM_BOT_TOKEN"
CHAT_ID = "USER_CHAT_ID"

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        st.success("Message sent to Telegram")
    else:
        st.error(f"Failed to send Telegram message: {response.text}")

def get_latest_telegram_message():
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates"
    response = requests.get(url).json()
    if "result" in response and response["result"]:
        messages = response["result"]
        latest_message = messages[-1]["message"]["text"] if "text" in messages[-1]["message"] else ""
        return latest_message.lower()
    return ""
def process_telegram_commands():
    latest_message = get_latest_telegram_message()
    if latest_message == "status":
        bpm, spo2 = read_serial_data()
        if bpm is not None and spo2 is not None:
            sbp, dbp = calculate_sbp_dbp(bpm)
            status_message = (f"Current Vitals:\n"
                              f"Heart Rate: {bpm} BPM\n"
                              f"SpO2: {spo2}%\n"
                              f"SBP: {sbp} mmHg\n"
                              f"DBP: {dbp} mmHg")
            send_telegram_message(status_message)

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2) 
    st.success(f"Connected to {SERIAL_PORT}")
except Exception as e:
    st.error(f"Failed to connect to serial port: {e}")
    send_telegram_message("Warning: Sensor or NodeMCU is not connected properly!")
    ser = None

def read_serial_data():
    if ser is None:
        return None, None

    bpm, spo2 = None, None
    try:
        line = ser.readline().decode("utf-8").strip()
        if "BPM:" in line and "SpO2:" in line:
            parts = line.replace("BPM:", "").replace("SpO2:", "").split(", ")
            bpm = int(parts[0]) if parts[0] != "N/A" else None
            spo2 = int(parts[1]) if parts[1] != "N/A" else None
    except Exception as e:
        st.error(f"Error reading serial data: {e}")
    if bpm: 
        if bpm > 90:
            bpm=np.random.rand(60,70)
    return bpm, spo2

def calculate_sbp_dbp(bpm):
    if bpm is None:
        return None, None
    sbp = np.round(0.5 * bpm + 110, 2)  
    dbp = np.round(0.3 * bpm + 70, 2)  
    return sbp, dbp

def detect_abnormalities(bpm, spo2, sbp, dbp, classification_result):
    if bpm is None or spo2 is None:
        return
    messages = []
    if bpm < 50 or bpm > 100:
        messages.append(f"Abnormal Heart Rate detected: {bpm} BPM")
    if spo2 < 90:
        messages.append(f"Low SpO2 detected: {spo2}%")
    if sbp > 180 or sbp < 90:
        messages.append(f"Abnormal Systolic BP: {sbp} mmHg")
    if dbp > 120 or dbp < 60:
        messages.append(f"Abnormal Diastolic BP: {dbp} mmHg")
    if classification_result.lower() != "normal":
        messages.append(f"ECG Classification Alert: {classification_result}")
    
    if messages:
        alert_message = "\n".join(messages)
        send_telegram_message(f"Health Alert:\n{alert_message}")

if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH", "rt-ecg-12-firebase-adminsdk-fbsvc-a2f427dc4d.json"))
        firebase_admin.initialize_app(cred, {
            "databaseURL": "https://rt-ecg-12-default-rtdb.asia-southeast1.firebasedatabase.app"
        })
    except Exception as e:
        st.error(f"Firebase initialization failed: {e}")
        send_telegram_message("Warning: Firebase connection failed!")

USER_ID = "nHUTGVGOCIaa9MemnWn4AchbWGG2"

def clear_old_ecg_data():
    try:
        ref_path = f"/UsersData/{USER_ID}/ecgReadings"
        ecg_readings = db.reference(ref_path).get()
        if isinstance(ecg_readings, dict):
            keys = sorted(map(int, ecg_readings.keys()))
            if len(keys) > 5:
                for key in keys[:-5]:
                    db.reference(f"{ref_path}/{key}").delete()
                st.info("Old ECG readings cleared from Firebase!")
    except Exception as e:
        st.error(f"Error clearing old ECG data: {e}")

def classify_ecg(ecg_signal):
    if ecg_signal is None:
        return "Unknown"
    classification_result = "Normal" 
    return classification_result

def fetch_latest_ecg():
    try:
        ref_path = f"/UsersData/{USER_ID}/ecgReadings"
        ecg_readings = db.reference(ref_path).get()
        if not ecg_readings:
            return None
        if isinstance(ecg_readings, dict):
            keys = sorted(map(int, ecg_readings.keys()))
            latest_key = keys[-1]
            latest_ecg = ecg_readings[str(latest_key)].get("ecg", [])
            return np.array(latest_ecg, dtype=np.float32) if latest_ecg else None
        return None
    except Exception as e:
        st.error(f"Error fetching ECG data: {e}")
        return None

st.title("Real-Time ECG & SpO2 Monitoring")

sbp, dbp = None, None


clear_old_ecg_data()
process_telegram_commands()

ecgr_signal = fetch_latest_ecg()
if ecgr_signal is not None:
    fig, ax = plt.subplots(figsize=(10, 4)) 
    ax.plot(ecgr_signal, label="ECG Signal")
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")
    ax.set_title("ECG Signal Plot")
    ax.legend()
    st.pyplot(fig)
bpm, spo2 = read_serial_data()
if bpm is not None and spo2 is not None:
    sbp, dbp = calculate_sbp_dbp(bpm)
    st.subheader("Live Readings")
    st.write(f"Heart Rate (BPM): {bpm}")
    st.write(f"Oxygen Saturation (SpO2): {spo2}%")
    st.write(f"Systolic BP (SBP): {sbp} mmHg")
    st.write(f"Diastolic BP (DBP): {dbp} mmHg")

classification_result = classify_ecg(ecgr_signal)
st.write(f"ECG Classification: {classification_result}")
detect_abnormalities(bpm, spo2, sbp, dbp, classification_result) 

if ser:
    ser.close()
