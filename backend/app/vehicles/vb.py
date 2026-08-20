import pika
import json
import time

from backend.app.services.memory import save_vehicle_memory


# =====================================
# RABBITMQ
# =====================================

connection = pika.BlockingConnection(
    pika.ConnectionParameters("localhost")
)

channel = connection.channel()


# =====================================
# EXCHANGE
# =====================================

channel.exchange_declare(
    exchange="vehicle_topics",
    exchange_type="topic",
    durable=True
)


# =====================================
# VEHICLE B QUEUE
# =====================================

channel.queue_declare(
    queue="vehicle_B_v3",
    durable=True
)

channel.queue_bind(
    exchange="vehicle_topics",
    queue="vehicle_B_v3",
    routing_key="to.B"
)


# =====================================
# VEHICLE B EVENTS
# =====================================

events = [

    {
        "vehicle_id": "B",
        "hazard": "accident",
        "confidence": 0.94,
        "recommendation": "slow_down"
    },

    {
        "vehicle_id": "B",
        "hazard": "pothole",
        "confidence": 0.89,
        "recommendation": "avoid_lane"
    }

]


print("\n================================")
print("🚗 VEHICLE B")
print("================================")


# =====================================
# SEND B → A
# =====================================

for event in events:

    channel.basic_publish(
        exchange="vehicle_topics",
        routing_key="to.A",
        body=json.dumps(event)
    )

    print("\n📤 Sent to Vehicle A:")
    print(event)

    time.sleep(1)


# =====================================
# RECEIVE A → B
# =====================================

received = []

print("\n👂 Waiting for Vehicle A...")


start_time = time.time()


while len(received) < 2:

    method, properties, body = channel.basic_get(
        queue="vehicle_B_v3",
        auto_ack=False
    )

    if method:

        data = json.loads(body.decode())

        received.append(data)

        print("\n📥 Received from Vehicle A:")
        print(data)


        # =================================
        # SAVE TO REDIS THROUGH BACKEND
        # =================================

        save_vehicle_memory(
            vehicle_id="B",
            source_vehicle=data["vehicle_id"],
            hazard=data["hazard"],
            confidence=data["confidence"],
            recommendation=data["recommendation"]
        )


        channel.basic_ack(
            delivery_tag=method.delivery_tag
        )

    else:

        time.sleep(0.5)


    # =================================
    # TIMEOUT
    # =================================

    if time.time() - start_time > 30:

        print("\n⚠️ Timeout waiting for Vehicle A.")

        break


# =====================================
# FINAL DECISION
# =====================================

print("\n================================")
print("🚗 VEHICLE B")
print("FINAL DECISION")
print("================================")


for data in received:

    hazard = data["hazard"]
    decision = data["recommendation"]

    print(
        hazard.upper(),
        "-",
        decision.upper()
    )


print("\n🧠 Vehicle B saved received hazards to Redis.")

connection.close()

print("\n✅ Vehicle B finished.")