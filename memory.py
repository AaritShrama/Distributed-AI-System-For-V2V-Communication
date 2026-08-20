import redis


r = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)


# =====================================
# VEHICLE A
# =====================================

print("\n================================")
print("🧠 VEHICLE A MEMORY")
print("================================")


keys = r.keys("vehicle:A:memory:*")


if not keys:

    print("No active memories.")

else:

    for key in keys:

        print("\nMemory:", key)

        print(
            "Data:",
            r.hgetall(key)
        )

        print(
            "TTL:",
            r.ttl(key),
            "seconds"
        )


# =====================================
# VEHICLE B
# =====================================

print("\n================================")
print("🧠 VEHICLE B MEMORY")
print("================================")


keys = r.keys("vehicle:B:memory:*")


if not keys:

    print("No active memories.")

else:

    for key in keys:

        print("\nMemory:", key)

        print(
            "Data:",
            r.hgetall(key)
        )

        print(
            "TTL:",
            r.ttl(key),
            "seconds"
        )