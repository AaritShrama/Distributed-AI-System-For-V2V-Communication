import h3
import time
import paho.mqtt.client as mqtt
from schema import SemanticMessage

# Device B current GPS position
CURRENT_LAT = 37.7749
CURRENT_LNG = -122.4194
def get_h3_topics(lat, lng, resolution=9):
    center_hex = h3.latlng_to_cell(lat, lng, resolution)
    regional_hexes = h3.grid_disk(center_hex, 1)
    return center_hex, [f"intelligence/{h}/#" for h in regional_hexes]
def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("\n✅ [System] Connected to MQTT Broker Successfully!")
        center_hex, topics = get_h3_topics(CURRENT_LAT, CURRENT_LNG)
        print(f"[Vehicle B] Location Hex: {center_hex}")
        for topic in topics:
            print(f"  [+] Subscribed to: {topic}")
            client.subscribe(topic)
    else:
        print(f"[System] Connection failed: {reason_code}")
def on_message(client, userdata, msg):
    try:
        raw_json = msg.payload.decode('utf-8')
        data: SemanticMessage = SemanticMessage.model_validate_json(raw_json)
        
        print("\n" + "="*50)
        print(f"[INTELLIGENCE RECEIVED] Topic: {msg.topic}")
        print(f" Vehicle ID    : {data.vehicle_id}")
        print(f" Event Type    : {data.event_type.upper()} ({data.object_type})")
        print(f" Risk Level    : {data.risk_level} (Confidence: {int(data.confidence * 100)}%)")
        print(f" Position      : ({data.position.latitude}, {data.position.longitude})")
        print(f" Description   : {data.description}")
        print(f" Recommendation: {data.recommendation.upper()}")
        print("="*50)
    except Exception as e:
        pass
# Using V2 API and HiveMQ public broker
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
print("Connecting to MQTT Broker...")
client.connect("broker.hivemq.com", 1883) 
client.loop_start()
print("\n[Vehicle B] Listening for semantic intelligence... Press Ctrl+C to exit.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    client.loop_stop()
    client.disconnect()