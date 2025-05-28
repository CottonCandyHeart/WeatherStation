import time
import threading
from paho.mqtt import client as mqtt_client
from influxdb_client import InfluxDBClient, Point, WritePrecision

# http://127.0.0.1:5000/

broker = 'test.mosquitto.org'
port = 1883
topics = [("KBDProjektTemp", 0), ("KBDProjektHum", 0), ("KBDProjektLDR", 0)]
client_id = f'weather-station'

# Dane współdzielone
latest_data = {"temp": 0, "hum": 0, "ldr": 0}

# InfluxDB config
url = "http://localhost:8086"
token = "y73z50WE8DbXTN7iE_8V0BxsnU5EVguxG4h0hmh9LbGXp5W-szdF6KoflTCXr4_MAdmZzmbzP7Tofos1dCyb9A=="
org = "PK"
bucket = "WeatherStation"
client_db = InfluxDBClient(url=url, token=token, org=org)
write_api = client_db.write_api()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ MQTT połączone")
        for topic, qos in topics:
            client.subscribe((topic, qos))
    else:
        print("❌ Błąd połączenia z MQTT")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print(f"Odebrano: {msg.topic} -> {payload}")


    now = time.time_ns()

    if msg.topic == "KBDProjektTemp":
        latest_data["temp"] = float(payload)
        point = Point("temperature").field("value", float(payload)).time(now, WritePrecision.NS)
    elif msg.topic == "KBDProjektHum":
        latest_data["hum"] = float(payload)
        point = Point("humidity").field("value", float(payload)).time(now, WritePrecision.NS)
    elif msg.topic == "KBDProjektLDR":
        latest_data["ldr"] = float(payload)
        point = Point("light").field("value", float(payload)).time(now, WritePrecision.NS)


def periodic_write():
    # Poczekaj minutę przed pierwszym zapisem
    time.sleep(60)
    while True:
        now = time.time_ns()
        print("🕒 Zapis danych do InfluxDB")
        points = [
            Point("temperature").field("value", latest_data["temp"]).time(now, WritePrecision.NS),
            Point("humidity").field("value", latest_data["hum"]).time(now, WritePrecision.NS),
            Point("light").field("value", latest_data["ldr"]).time(now, WritePrecision.NS)
        ]
        write_api.write(bucket=bucket, org=org, record=points)
        time.sleep(1800)  # kolejne zapisy co 30 minut
def start_mqtt():
    def _run():
        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker, port, keepalive=60)
        client.loop_forever()

    threading.Thread(target=_run, daemon=True).start()
    threading.Thread(target=periodic_write, daemon=True).start()
