import paho.mqtt.client as mqtt
import time
import sys

# Define the MQTT Broker address and port
broker_address = "test.mosquitto.org"  # You can also use other MQTT Brokers
broker_port = 1883
topic = "test/topic"
connected = False

# Define callback functions
def on_connect(client, userdata, flags, rc):
    global connected
    print(f"Connected with result code {rc}")
    client.subscribe(topic)
    connected = True

def on_message(client, userdata, msg):
    print(f"Received message:\n\ttopic: {msg.topic}\n\tpayload: {msg.payload.decode()}")

def on_publish(client, userdata, mid):
    print(f"Message id {mid} published.")

# Create MQTT client instance
client = mqtt.Client()

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish

# Connect to MQTT Broker
client.connect(broker_address, broker_port, 60)

# Start the client's network loop
client.loop_start()

t = time.time()
while not connected:
    if time.time() - t > 5:
        print("wait connect time out")
        sys.exit(-1)
    time.sleep(0.1)

# Publish a message
client.publish(topic, "Hello MQTT")

# Wait for a while to ensure the message is received
time.sleep(10)

# Stop the client's network loop and disconnect
client.loop_stop()
client.disconnect()
