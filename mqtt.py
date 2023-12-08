import paho.mqtt.client as mqtt
import json
import socket

class VServer:
    def __init__(self, port):
        self.port = port
        self.mqtt_broker = mqtt.Client()
        self.mqtt_broker.on_connect = self.on_broker_connect

    def on_broker_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"VServer connected to MQTT broker on port {self.port}")
        else:
            print(f"Failed to connect to MQTT broker with code {rc}")

    def start(self):
        self.mqtt_broker.bind("localhost", self.port)
        self.mqtt_broker.listen(5)
        print(f"VServer listening on port {self.port}")
        self.mqtt_broker.loop_forever()

class VNode:
    def __init__(self, name, mqtt_port):
        self.name = name
        self.mqtt_port = mqtt_port
        self.host = socket.gethostbyname(socket.gethostname())
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"{self.name} connected to MQTT broker.")
            self.subscribe_to_events()
        else:
            print(f"Failed to connect to MQTT broker with code {rc}")

    def on_message(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        print(f"Received message: {payload}")

    def subscribe_to_events(self):
        topic = "vnode_events"
        self.mqtt_client.subscribe(topic)
        print(f"{self.name} subscribed to {topic}")

    def publish_start_message(self):
        topic = "vnode_events"
        message = {"event": "start", "name": self.name, "host": self.host}
        self.mqtt_client.publish(topic, json.dumps(message))

    def publish_stop_message(self):
        topic = "vnode_events"
        message = {"event": "stop", "name": self.name, "host": self.host}
        self.mqtt_client.publish(topic, json.dumps(message))

    def start(self):
        self.mqtt_client.connect("localhost", self.mqtt_port, 60)
        self.mqtt_client.loop_start()

    def stop(self):
        self.publish_stop_message()
        self.mqtt_client.disconnect()

# Example usage:
vserver = VServer(port=1883)
vserver.start()

vnode1 = VNode(name="VNode1", mqtt_port=1883)
vnode1.start()

# Simulate VNode running for a while
# ...

vnode1.stop()
