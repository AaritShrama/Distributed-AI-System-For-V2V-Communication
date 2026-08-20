import pika
import redis
import json
import time


# =====================================
# REDIS
# =====================================

r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


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
# VEHICLE A QUEUE
# =====================================

channel.queue_declare(
    queue="vehicle_A_v3",
    durable=True
)

channel.queue_bind(
    exchange="vehicle_topics",
    queue="vehicle_A_v3",
    routing_key="to.A"
)


# =====================================
# VEHICLE A EVENTS
# =====================================

events = [

    {
        "vehicle_id": "A",
        "hazard": "pedestrian",
        "confidence": 0.96,
        "recommendation": "slow_down"
    },

    {
        "vehicle_id": "A",
        "hazard": "oil_spill",
        "confidence": 0.91,
        "recommendation": "change_lane"
    }

]


print("\n================================")
print("🚗 VEHICLE A")
print("================================")


# =====================================
# SEND A → B
# =====================================

for event in events:

    channel.basic_publish(
        exchange="vehicle_topics",
        routing_key="to.B",
        body=json.dumps(event)
    )

    print("\n📤 Sent to Vehicle B:")
    print(event)

    time.sleep(1)


# =====================================
# RECEIVE B → A
# =====================================

received = []

print("\n👂 Waiting for Vehicle B...")


start_time = time.time()


while len(received) < 2:

    method, properties, body = channel.basic_get(
        queue="vehicle_A_v3",
        auto_ack=False
    )

    if method:

        data = json.loads(body.decode())

        received.append(data)

        print("\n📥 Received from Vehicle B:")
        print(data)

        # Save to Redis
        hazard = data["hazard"]

        key = "vehicle:A:memory:" + hazard

        r.hset(
            key,
            mapping={
                "source_vehicle": data["vehicle_id"],
                "hazard": data["hazard"],
                "confidence": str(data["confidence"]),
                "recommendation": data["recommendation"]
            }
        )

        r.expire(key, 30)

        channel.basic_ack(
            delivery_tag=method.delivery_tag
        )

    else:

        time.sleep(0.5)


    # Safety timeout
    if time.time() - start_time > 30:

        print("\n⚠️ Timeout waiting for Vehicle B.")

        break


# =====================================
# FINAL DECISION
# =====================================

print("\n================================")
print("🚗 VEHICLE A")
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


print("\n🧠 Vehicle A saved received hazards to Redis.")

connection.close()

print("\n✅ Vehicle A finished.")