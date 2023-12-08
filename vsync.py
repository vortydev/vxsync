import socket
import multiprocessing
import time
import signal
import sys

class VNode:
    def __init__(self, name: str, port: int=5555):
        self.name = name
        self.host = socket.gethostname()
        self.port = port
        self.node_comms = NodeComms(self)
        self.node_comms.start_receiver_process()

    def display_info(self):
        print(f"VNode Name: {self.name}")
        print(f"Host: {self.host}")
        print(f"Port: {self.port}")


class NodeComms:
    def __init__(self, node: VNode):
        self.node = node
        self.receive_process = None

    def send_message(self, message: str, target_node: VNode):
        host, port = target_node.host, target_node.port
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

                    # Check if it's a ping request
                    if received_message.lower() == "ping request":
                        self.ping_answer(addr)

                    # Add your custom handling logic here

                except KeyboardInterrupt:
                    print("Keyboard interrupt received. Exiting.")
                    sys.exit(0)

    def start_receiver_process(self):
        self.receive_process = multiprocessing.Process(target=self.receive_message)
        self.receive_process.start()

    def stop_receiver_process(self):
        if self.receive_process:
            self.receive_process.terminate()
            self.receive_process.join()

    def ping_send(self, target_node, message="Ping request"):
        self.send_message(message, target_node)

    def ping_answer(self, addr):
        response_message = f"Ping response from {self.node.name}"
        self.send_message(response_message, VNode(host=addr[0], port=addr[1]))

# Example usage:
if __name__ == "__main__":
    # Register a signal handler for graceful exit
    signal.signal(signal.SIGINT, lambda signal, frame: sys.exit(0))

    # Create VNode instance
    my_node = VNode(name="Solertia")

    # Display node information
    my_node.display_info()

    # Example usage of communication and ping
    target_node = VNode(name="TargetVNode")
    
    # Send a message
    my_node.node_comms.send_message("Hello, TargetVNode!", target_node)

    # Ping another node
    my_node.node_comms.ping_send(target_node)

    # Stop the receiver process
    my_node.node_comms.stop_receiver_process()
