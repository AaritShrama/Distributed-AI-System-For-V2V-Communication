import h3
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from schema import SemanticMessage, Position

# Target hazard location (placed in Vehicle B's region)
HAZARD_LAT = 37.7750
HAZARD_LNG = -122.4190

target_hex = h3.latlng_to_cell(HAZARD_LAT, HAZARD_LNG, res=9)
topic = f"intelligence/{target_hex}/hazard"

message = SemanticMessage(
    vehicle_id="Vehicle_A_Node",
    event_type="hazard",
    object_type="pedestrian_blind_spot",
    confidence=0.96,
    risk_level="CRITICAL",
    position=Position(latitude=HAZARD_LAT, longitude=HAZARD_LNG),
    description="Pedestrian stepping out behind blind corner.",
    recommendation="hard_brake",
    timestamp=datetime.now(timezone.utc)
)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("broker.hivemq.com", 1883)

print(f"\n[Vehicle A] Publishing hazard intelligence to Hex: {target_hex}")
client.publish(topic, message.model_dump_json())
print("[Vehicle A] Message Sent Successfully!")

client.disconnect()