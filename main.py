import time
from PIL import Image
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from influxdb_client import InfluxDBClient, Point, WritePrecision
from paho.mqtt import client as mqtt_client
from io import BytesIO
import base64
import random

# http://localhost:8501
# streamlit run /Users/veronica/PycharmProjects/WeatherStation/main.py
# ----------------- Konfiguracja strony -----------------
st.set_page_config(page_title="Stacja pogodowa", layout="centered")
st.title("🌤️ Domowa stacja pogodowa")

# ----------------- Auto-odświeżenie co 1s -----------------
st_autorefresh(interval=1000, key="auto-refresh")

# ----------------- Stan aplikacji -----------------
if "temp" not in st.session_state:
    st.session_state.temp = "0"
if "hum" not in st.session_state:
    st.session_state.hum = "0"
if "ldr" not in st.session_state:
    st.session_state.ldr = "0"
if "mqtt_connected" not in st.session_state:
    st.session_state.mqtt_connected = False

# ----------------- Funkcje ikon -----------------
def get_temp_icon(temp):
    temp = float(temp)
    return "img/temp/cold-btl.png" if temp < 20 else "img/temp/hot-btl.png"

def get_hum_icon(hum):
    hum = float(hum)
    if hum < 30:
        return "img/hum/low.png"
    elif hum < 60:
        return "img/hum/normal.png"
    else:
        return "img/hum/high.png"

def get_ldr_icon(ldr):
    ldr = float(ldr)
    if ldr < 200:
        return "img/ldr/low.png"
    elif ldr < 500:
        return "img/ldr/medium.png"
    else:
        return "img/ldr/high.png"

# ----------------- Konfiguracja obrazków -----------------
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def show_centered_image(img):
    img_str = image_to_base64(img)
    st.markdown(
        f"<div style='text-align:center'><img src='data:image/png;base64,{img_str}'/></div>",
        unsafe_allow_html=True,
    )

# ----------------- Baza danych konfiguracja -----------------
url = "http://localhost:8086"
token = "LXvm5kID0pfEWrOTcrQ4c8Iu0QhAAxW6DBhiCCCR53zmqRZWFGewmbvP5uXWEy-lM7k72qEPJnk_vBe53PTc4g=="
org = "WeatherStation"
bucket = "WeatherStation"

client_db = InfluxDBClient(url=url, token=token, org=org)

# ----------------- MQTT konfiguracja -----------------
broker = 'test.mosquitto.org'
port = 1883
topics = [("KBDProjektTemp", 0), ("KBDProjektHum", 0), ("KBDProjektLDR", 0)]
client_id = f'weather-station-{random.randint(1000, 9999)}'  # Uproszczony client_id

mqtt_error_codes = {
    0: "Połączenie udane",
    1: "Nieprawidłowa wersja protokołu",
    2: "Nieprawidłowy identyfikator klienta",
    3: "Serwer niedostępny",
    4: "Zła nazwa użytkownika/hasło",
    5: "Brak autoryzacji"
}

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Połączono z MQTT brokerem!")
        for topic, qos in topics:
            client.subscribe((topic, qos))
            print(f"Subskrybowano temat: {topic}")
        st.session_state.mqtt_connected = True
    else:
        error_msg = mqtt_error_codes.get(rc, f"Nieznany kod błędu: {rc}")
        print(f"❌ Błąd połączenia MQTT: {error_msg}")
        st.session_state.mqtt_connected = False

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        print(f"📩 Odebrano z {msg.topic}: {payload}")

        write_api = client_db.write_api()

        if msg.topic == "KBDProjektTemp":
            st.session_state.temp = payload
            point = Point("temperature").field("value", float(payload)).time(time.time_ns(), WritePrecision.NS)
            write_api.write(bucket=bucket, org=org, record=point)

        elif msg.topic == "KBDProjektHum":
            st.session_state.hum = payload
            point = Point("humidity").field("value", float(payload)).time(time.time_ns(), WritePrecision.NS)
            write_api.write(bucket=bucket, org=org, record=point)

        elif msg.topic == "KBDProjektLDR":
            st.session_state.ldr = payload
            point = Point("light").field("value", float(payload)).time(time.time_ns(), WritePrecision.NS)
            write_api.write(bucket=bucket, org=org, record=point)

    except Exception as e:
        print(f"❌ Błąd w on_message: {e}")

def connect_mqtt():
    try:
        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker, port)
        client.loop_start()
        return client
    except Exception as e:
        print(f"❌ Nie można połączyć z MQTT: {e}")
        return None

# ----------------- Łączenie z MQTT -----------------
if "mqtt_client" not in st.session_state:
    st.session_state.mqtt_client = connect_mqtt()

# ----------------- Tymczasowe dane testowe -----------------
if st.session_state.temp == "0":
    st.session_state.temp = 0
    st.session_state.hum = 0
    st.session_state.ldr = 0

# ----------------- UI z kolumnami -----------------
col1, col2, col3 = st.columns(3)

# ----------------- Pobranie danych -----------------
try:
    temp = float(st.session_state.temp)
    hum = float(st.session_state.hum)
    ldr = float(st.session_state.ldr)
except ValueError:
    temp, hum, ldr = 0.0, 0.0, 0.0

# ----------------- Ikony -----------------
temp_icon = get_temp_icon(temp)
hum_icon = get_hum_icon(hum)
ldr_icon = get_ldr_icon(ldr)

# ----------------- Wyświetlanie danych -----------------
with col1:
    st.metric("🌡️ Temperatura", f"{temp} °C")
    img = Image.open(temp_icon)
    img = img.resize((int(img.width * 100 / img.height), 100))
    show_centered_image(img)

with col2:
    st.metric("💧 Wilgotność", f"{hum} %")
    img = Image.open(hum_icon)
    img = img.resize((int(img.width * 100 / img.height), 100))
    show_centered_image(img)

with col3:
    st.metric("🔆 Naświetlenie", f"{ldr} lx")
    img = Image.open(ldr_icon)
    img = img.resize((int(img.width * 100 / img.height), 100))
    show_centered_image(img)

# ----------------- Status połączenia -----------------
st.sidebar.markdown("### Status systemu")
if st.session_state.mqtt_connected:
    st.sidebar.success("✅ Połączono z MQTT")
else:
    st.sidebar.error("❌ Brak połączenia z MQTT")