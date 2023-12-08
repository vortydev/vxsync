import socket
import threading

SERVER_IP = "localhost"

# Event to signal threads to terminate
exit_event = threading.Event()

def receive_messages(client_socket: socket.socket, address):
    try:
        while not exit_event.is_set():
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print(f"Connection with {address} closed.")
                break
            print(f"Received message from {address}: {message}")

            if message.lower() == 'stop':
                print("Received 'stop' command. Closing all connections...")
                exit_event.set()
                break

    except ConnectionResetError:
        print(f"Connection with {address} reset by the client.")
    except Exception as e:
        print(f"Error receiving message from {address}: {e}")
    finally:
        client_socket.close()


def send_messages(client_socket: socket.socket):
    try:
        while not exit_event.is_set():
            message = input("Enter a message (type 'exit' to close connection): ")
            client_socket.send(message.encode('utf-8'))
            if message.lower() == 'exit':
                break   
    except Exception as e:
        print(f"Error sending message: {e}")
    finally:
        client_socket.close()


def handle_client(client_socket: socket.socket, address):
    print(f"Accepted connection from {address}")

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, address))
    send_thread = threading.Thread(target=send_messages, args=(client_socket,))

    try:
        receive_thread.start()
        send_thread.start()
        receive_thread.join()
        send_thread.join()
    except KeyboardInterrupt:
        print(f"\nConnection with {address} interrupted.")
        exit_event.set()
    finally:
        print(f"Closing connection with {address}")
        client_socket.close()
