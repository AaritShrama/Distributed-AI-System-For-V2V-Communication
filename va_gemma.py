import ollama
import paho.mqtt.client as mqtt
import json
import time

# --- MQTT SETUP ---
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 8000
MQTT_TOPIC = "v2v/alerts/tokyodrifters"

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, transport="websockets")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

def process_and_send(sensor_data):
    print("[Vehicle A] Analyzing sensor data with local AI...")
    
    prompt = f"""
    You are an AI in a car (Vehicle A). Analyze this sensor data: {json.dumps(sensor_data)}
    If there is a hazard, write a strictly short, 1-sentence warning for the car behind us.
    If it is safe, reply 'Clear'.
    """

    response = ollama.chat(model='gemma2:2b', messages=[
        {'role': 'user', 'content': prompt}
    ])
    
    ai_decision = response['message']['content'].strip()
    print(f"[Vehicle A] AI Output: {ai_decision}")
    
    if "Clear" not in ai_decision:
        payload = json.dumps({"sender": "Vehicle_A", "warning": ai_decision})
        print(f"[Vehicle A] Broadcasting via MQTT: {payload}")
        client.publish(MQTT_TOPIC, payload)

if __name__ == "__main__":
    simulated_data = {
        "speed_kmh": 80,
        "radar": "Sudden hard braking detected in front",
        "weather": "Clear"
    }
    process_and_send(simulated_data)
    time.sleep(2)