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
token = "LXvm5kID0pfEWrOTcrQ4c8Iu0QhAAxW6DBhiCCCR53zmqRZWFGewmbvP5uXWEy-lM7k72qEPJnk_vBe53PTc4g=="
org = "WeatherStation"
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

    #write_api = client_db.write_api()
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

    write_api.write(bucket=bucket, org=org, record=point)


def start_mqtt():
    def _run():
        client = mqtt_client.Client(client_id)
        client.on_connect = on_connect
        client.on_message = on_message
        client.connect(broker, port, keepalive=60)
        client.loop_forever()

    threading.Thread(target=_run, daemon=True).start()
