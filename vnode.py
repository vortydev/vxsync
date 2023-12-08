# vnode.py
import socket
import multiprocessing
import sys
import time


class VNode:
    def __init__(self, name, port=5555):
        self.name = name
        self.host = socket.gethostname()
        self.port = port
        self.comms = NodeComms(self)
        self.comms.start_receiver_process()

    def display_info(self):
        print(f"VNode Name: {self.name}")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")



class NodeComms:
    def __init__(self, node: VNode):
        self.node = node
        self.receive_process = None
        self.online_nodes: set[VNode] = set()  # Set to store online nodes

    def send_message(self, message: str, host: str, port: int):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(message.encode('utf-8'), (host, port))

    def receive_message(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind((self.node.host, self.node.port))
            while True:
                try:
                    data, addr = s.recvfrom(1024)
                    received_message = data.decode('utf-8')
                    print(f"Received message from {addr}: {received_message}")

                    # Check if it's an online message
                    if received_message.lower() == "online":
                        self.add_online_node(addr)

                    # Check if it's an offline message
                    elif received_message.lower() == "offline":
                        self.remove_online_node(addr)

                    elif received_message.lower() == "ping":
                        self.ping_answer(addr)

                    # Add your custom handling logic here

                except KeyboardInterrupt:
                    print("Keyboard interrupt received. Exiting.")
                    self.broadcast_offline()  # Broadcast offline before exiting
                    sys.exit(0)

    def start_receiver_process(self):
        self.receive_process = multiprocessing.Process(target=self.receive_message)
        self.receive_process.start()

    def stop_receiver_process(self):
        if self.receive_process:
            self.receive_process.terminate()
            self.receive_process.join()

    def ping_send(self, target_node: VNode, message="ping"):
        self.send_message(message, target_node.host, target_node.port)

    def ping_answer(self, addr):
        response_message = f"Ping response from {self.node.name}"
        self.send_message(response_message, addr[0], addr[1])

    def broadcast_online(self):
        self.send_message("online", None, None)

    def broadcast_offline(self):
        self.send_message("offline", target_node=None)

    def add_online_node(self, addr):
        online_node = VNode(host=addr[0], port=addr[1])
        self.online_nodes.add(online_node)
        print(f"Node {online_node.name} is online.")

    def remove_online_node(self, addr):
        offline_node = VNode(host=addr[0], port=addr[1])
        if offline_node in self.online_nodes:
            self.online_nodes.remove(offline_node)
            print(f"Node {offline_node.name} is offline.")