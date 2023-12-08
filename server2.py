import socket
import threading

SERVER_IP = "localhost"
SERVER_PORT = 5555

# Event to signal threads to terminate
exit_event = threading.Event()

def receive_messages(client_socket: socket.socket):
    try:
        while not exit_event.is_set():
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("Connection closed.")
                break
            print(f"Received message: {message}")

            # Check for the "stop" command
            if message.lower() == 'stop':
                print("Received 'stop' command. Closing all connections...")
                exit_event.set()  # Set the event to signal threads to exit
                break  # Break out of the loop to close the connection

    except ConnectionResetError:
        print("Connection reset by the client.")
    except Exception as e:
        print(f"Error receiving message: {e}")
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

def main():
    # Set up the server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((SERVER_IP, SERVER_PORT))
    server.listen(5)

    print("Server listening for connections...")

    try:
        # Accept connections in a loop
        while not exit_event.is_set():
            client, addr = server.accept()
            print(f"Accepted connection from {addr}")

            receive_thread = threading.Thread(target=receive_messages, args=(client,))
            send_thread = threading.Thread(target=send_messages, args=(client,))

            receive_thread.start()
            send_thread.start()

            receive_thread.join()
            send_thread.join()

    except KeyboardInterrupt:
        print("\nServer shutting down...")
        exit_event.set()  # Set the event to signal threads to exit
        server.close()  # Close the server socket
        exit()

if __name__ == "__main__":
    main()
