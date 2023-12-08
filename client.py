# client.py

# Packages
import socket
import threading

# ENV
SERVER_IP = "localhost"
SERVER_PORT = 5555

def receive_messages(client_socket: socket.socket):
    """Receive messages on a connected socket. """
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("Connection closed by the server.")
                break
            print(f"Server: {message}")

            # Check for the "exit" command
            if message.lower() == 'exit':
                print("Server requested to close connection.")
                client_socket.close()
                break

    except ConnectionResetError:
        print("Connection reset by the server.")
    except Exception as e:
        print(f"Error receiving message from the server: {e}")
    finally:
        client_socket.close()

def main():
    # Set up the client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))

    # Get the client's name
    name = input("Enter your name: ")
    client.send(name.encode('utf-8'))

    # Start a thread to receive messages from the server
    receive_thread = threading.Thread(target=receive_messages, args=(client,))
    receive_thread.start()

    try:
        while True:
            message = input("Enter a message (type 'exit' to close connection): ")
            client.send(message.encode('utf-8'))
            if message.lower() == 'exit':
                receive_thread.join()
                client.close()
                break

    except KeyboardInterrupt:
        print("\nClient shutting down...")

        if (client):
            # Send 'exit' command to the server before closing connection
            client.send('exit'.encode('utf-8'))

            # Wait for the receive thread to finish
            receive_thread.join()

            # Close the client
            client.close()

    finally:
        exit(0)
            


if __name__ == "__main__":
    main()
