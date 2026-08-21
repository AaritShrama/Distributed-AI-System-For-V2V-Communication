from backend.app.core.redis import get_redis


# ============================================
# SAVE VEHICLE MEMORY
# ============================================

def save_vehicle_memory(
    vehicle_id: str,
    source_vehicle: str,
    hazard: str,
    confidence: float,
    recommendation: str,
    ttl: int = 30,
):

    redis_client = get_redis()

    key = f"vehicle:{vehicle_id}:memory:{hazard}"

    redis_client.hset(
        key,
        mapping={
            "source_vehicle": source_vehicle,
            "hazard": hazard,
            "confidence": str(confidence),
            "recommendation": recommendation,
        }
    )

    # Automatically expire memory after 30 seconds
    redis_client.expire(key, ttl)

    print(
        f"🧠 Redis memory saved: {key} "
        f"(expires in {ttl} seconds)"
    )


# ============================================
# GET VEHICLE MEMORY
# ============================================

def get_vehicle_memory(vehicle_id: str, hazard: str):

    redis_client = get_redis()

    key = f"vehicle:{vehicle_id}:memory:{hazard}"

    return redis_client.hgetall(key)


# ============================================
# DELETE VEHICLE MEMORY
# ============================================

def delete_vehicle_memory(vehicle_id: str, hazard: str):

    redis_client = get_redis()

    key = f"vehicle:{vehicle_id}:memory:{hazard}"

    redis_client.delete(key)


# ============================================
# DISPLAY VEHICLE MEMORIES
# ============================================

def display_vehicle_memory(vehicle_id: str):

    redis_client = get_redis()

    pattern = f"vehicle:{vehicle_id}:memory:*"

    keys = redis_client.keys(pattern)

    print("\n================================")
    print(f"🚗 VEHICLE {vehicle_id} MEMORY")
    print("================================")

    if not keys:
        print("No active memories.")
        return

    for key in keys:

        data = redis_client.hgetall(key)

        ttl = redis_client.ttl(key)

        print("\n------------------------------")

        print(f"Hazard        : {data.get('hazard', 'N/A')}")
        print(f"Source Vehicle: {data.get('source_vehicle', 'N/A')}")
        print(f"Confidence    : {data.get('confidence', 'N/A')}")
        print(f"Recommendation: {data.get('recommendation', 'N/A')}")

        if ttl >= 0:
            print(f"TTL           : {ttl} seconds")
        else:
            print("TTL           : No expiration")


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":

    print("\n================================")
    print("🧠 VEHICLE MEMORY SYSTEM")
    print("================================")

    # Vehicle A
    display_vehicle_memory("A")

    # Vehicle B
    display_vehicle_memory("B")

    print("\n================================")
    print("✅ MEMORY CHECK COMPLETE")
    print("================================")