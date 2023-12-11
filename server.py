# server.py

# Packages
import socket
import threading
import select
import time

# ENV
SERVER_IP = "localhost"
SERVER_PORT = 5555
MAX_CONNECTIONS = 5


# Event to signal threads to terminate
exit_event = False

# Dictionary to store active connections and their names
active_connections: dict[any, tuple[str, socket.socket]] = {}

# Create a lock for thread safety
active_connections_lock = threading.Lock()


def process_client_message(name: str, address, message: str, client_socket: socket.socket):
    """
    Process messages received from a client.
    """
    global active_connections

    if message.lower() == 'exit':
        print(f"{name} at {address} requested to close connection.")
        return True  # Signal to close the connection
    
    elif message.lower() == 'ping':
        client_socket.send('pong'.encode('utf-8'))
        print(f"Responded to {name}'s ping at {address}.")
        return False

    elif message.lower() == 'list':
        print(f"\nActive connections ({len(active_connections)}):")
        count = 0
        for addr, (name, _) in active_connections.items():
            count += 1
            print(f"{count}. {name} {addr}")
    
    return False


def handle_client(client_socket: socket.socket, address):
    try:
        # Receive the client's name
        name = client_socket.recv(1024).decode('utf-8')
        print(f"Connection established with {name} at {address}")

        # Store the active connection
        active_connections[address] = (name, client_socket)

        while not exit_event:
            message = client_socket.recv(1024).decode('utf-8')
            with active_connections_lock:
                if not message:
                    print(f"Connection with {name} at {address} closed.")
                    break
                print(f"Received message from {name} at {address}: {message}")

                if process_client_message(name, address, message, client_socket):
                    break

    except ConnectionResetError:
        print(f"Connection with {name} at {address} reset by the client.")
    except Exception as e:
        if not exit_event:
            print(f"Error handling client {name} at {address}: {e}")

    finally:
        with active_connections_lock:
            # Remove the connection from the active list
            del active_connections[address]
        client_socket.close()


def main():
    global exit_event

    # Set up the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(MAX_CONNECTIONS)

    print("Server listening for connections...")

    try:
        # Accept connections in a loop
        while not exit_event:
            # Use select to check for incoming connections and KeyboardInterrupt
            inputs, _, _ = select.select([server], [], [], 1)  # 1-second timeout

            if server in inputs:
                # Accept connections
                client, addr = server.accept()
                print(f"Accepted connection from {addr}")

                # Start a thread to handle the client
                client_handler = threading.Thread(target=handle_client, args=(client, addr))
                client_handler.start()

    except KeyboardInterrupt:
        print("\nServer shutting down...")

        # Notify active clients to close connections
        for address, (name, client_socket) in active_connections.items():
            print(f"Sending 'exit' command to {name} at {address}")
            try:
                client_socket.send('exit'.encode('utf-8'))
            except Exception as e:
                print(f"Error sending 'exit' command to {name} at {address}: {e}")
                continue

        exit_event = True   # Set the event to signal server to exit
        server.close()      # Close the server socket
        exit()

if __name__ == "__main__":
    main()
