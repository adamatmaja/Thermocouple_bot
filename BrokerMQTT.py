import json
from datetime import datetime
import time
import pyodbc
import paho.mqtt.client as mqtt

# ==============================
# KONFIGURASI
# ==============================
MQTT_BROKER = "1.1.0.1"       
MQTT_PORT   = 1234
MQTT_TOPIC  = "tes/tele/#"        

SQL_CONN_STR = (
    ""
)

RECONNECT_DELAY = 5  # detik

# ==============================
# FUNGSI DATABASE
# ==============================
def insert_to_db(device_id, ts_utc, temp_c, status, rssi=None):
    try:
        cursor.execute("""
            INSERT INTO dbo.telemetry_temp (device_id, ts_utc, temp_c, status, rssi)
            VALUES (?, ?, ?, ?, ?)
        """, (device_id, ts_utc, temp_c, status, rssi))
        conn.commit()
        print(f"[DB] {ts_utc} | {device_id} | {temp_c:.2f} °C | status={status} | rssi={rssi}")
    except Exception as e:
        print("[DB ERROR]", e)
        conn.rollback()


# ==============================
# HANDLER MQTT
# ==============================
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("[MQTT] Connected OK")
        client.subscribe(MQTT_TOPIC)
        print(f"[MQTT] Subscribed to '{MQTT_TOPIC}'")
    else:
        print(f"[MQTT] Connection failed with code {rc}")

        
def on_msg(client,userdata,msg):
    try:
        payload = json.loads(msg.payload.decode())
        device_id = msg.topic.split("/")[-1]
        temp_c = float(payload["temperature"])
        ts_utc = datetime.now()
        status = int(payload.get("status", 0))
        rssi = payload.get("rssi", None)
        insert_to_db(device_id, ts_utc, temp_c, status, rssi)
    except Exception as e:
        print("[PARSE ERROR]", e, "| RAW:", msg.payload)
        
def on_disconnect(client, userdata, rc):
    print(f"[MQTT] Disconnected (code {rc}), reconnecting in {RECONNECT_DELAY}s...")
    time.sleep(RECONNECT_DELAY)
    try:
        client.reconnect()
    except:
        print("[MQTT] Reconnect failed, retrying...")

# ==============================
# MAIN PROGRAM
# ==============================
print("[INIT] Connecting to SQL Server...")
conn = pyodbc.connect(SQL_CONN_STR, autocommit=False)
cursor = conn.cursor()
print("[INIT] SQL connection OK")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_msg
client.on_disconnect = on_disconnect

print(f"[INIT] Connecting to MQTT broker {MQTT_BROKER}:{MQTT_PORT} ...")
client.connect(MQTT_BROKER,MQTT_PORT)

print("Running")
client.loop_forever()
