import json
from datetime import datetime
import paho.mqtt.client as mqtt

MQTT_BROKER = "1.1.1.2"
MQTT_PORT = 1883
MQTT_TOPIC = "TOP/tele/#"

def on_connect(client, userdata, flags, rc):
    print("[MQTT] on_connect rc =",rc)
    if rc ==0:
        client.subscriber(MQTT_TOPIC)
        print(f"[MQTT] Subscribed to {MQTT_TOPIC}")
    else:
        print("[MQTT] Connection Failed")

def on_message(client,usedata,msg):
    print("\n[MQTT IN")
    print("Topic :", msg.topic)
    print("Payload:",msg.payload)

    try:
        payload = json.loads(msg.payload.decode())
        device_id = payload["device_id"]
        temperature = float(payload["temperature"])
        ts = datetime.utcnow()
        print = (f"[DATA] {ts} | {device_id} | {temperature:.2f} C") 
    except Exception as e:
        print("[PARSE ERROR]",e)

def on_disconnect(client, userdata, rc):
    print("[MQTT] DISCONNECTED rc=",rc)

print("====STARTED====")
client = mqtt.Client()
client.onconnect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.connect(MQTT_BROKER,MQTT_PORT)
client.loop_forever()
