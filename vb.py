import paho.mqtt.client as mqtt
import json

# --- MQTT SETUP ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 8000
MQTT_TOPIC = "v2v/alerts/tokyodrifters"

def on_connect(client, userdata, flags, rc):
    print(f"[Vehicle B] Connected to V2V Network. Listening for alerts...")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print("\n" + "="*40)
    print(f"🚨 ALERT RECEIVED FROM {data['sender']} 🚨")
    print(f"Message: {data['warning']}")
    print("="*40 + "\n")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, transport="websockets")
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()