import random
import time

def read_sensor():
    # Simulated DHT sensor readings; replace with real sensor integration.
    return round(random.uniform(20, 38), 1), round(random.uniform(30, 85), 1)

print("Smart Room Monitor (simulation)")
for _ in range(10):
    temperature, humidity = read_sensor()
    status = "ALERT: High temperature" if temperature >= 35 else "Normal"
    print(f"Temperature: {temperature} C | Humidity: {humidity}% | {status}")
    time.sleep(1)
