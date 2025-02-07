import socket

def create_socket():
    # Creating TCP/IP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    return client_socket

def connect_to_server(client_socket, server_ip, server_port):
    # Connecting the socket to the server's address
    try:
        client_socket.connect((server_ip, server_port))
        print("client: Connected to server.")
    except Exception as e:
        print(f"client: Failed to connect to server: {e}")
        exit()

def send_command(client_socket, command):
    # Send a command to the server
    client_socket.sendall(command.encode('utf-8'))

def post_content(client_socket):
    # Handling the POST command
    while True:
        line = input("client: ")
        send_command(client_socket, line)
        if line == "#":
            break

def delete_messages(client_socket):
    # Handling the DELETE command
    while True:
        msg_id = input("client: ")
        send_command(client_socket, msg_id)
        if msg_id == "#":
            break

def receive_response(client_socket):
    # Receive a response from the server
    response = client_socket.recv(4096).decode('utf-8')
    return response

def close_socket(client_socket):
    # Closing the socket connection
    client_socket.close()
    

def handle_response(client_socket):
    # Handling the server's response
    response = receive_response(client_socket)
    if response == 'OK':
        print("server: OK")
    else:
        print("server:", response)

def main():
    # Main function to run the client
    server_ip = input("Enter server IP: ")
    server_port = int(input("Enter server port: "))

    client_socket = create_socket()
    connect_to_server(client_socket, server_ip, server_port)

    try:
        while True:
            command = input("client: ").strip().upper()

            if command == 'POST':
                send_command(client_socket, 'POST')
                post_content(client_socket)
                handle_response(client_socket)

            elif command == 'GET':
                send_command(client_socket, 'GET')
                while True:
                    response = receive_response(client_socket)
                    if response == "#":
                        print("server: #")
                        break
                    print("server:", response)

            elif command == 'DELETE':
                send_command(client_socket, 'DELETE')
                delete_messages(client_socket)
                handle_response(client_socket)

            elif command == 'QUIT':
                send_command(client_socket, 'QUIT')
                handle_response(client_socket)
                close_socket(client_socket)
                break

            else:
                print("client: WRONG COMMAND")
                send_command(client_socket, command)
                response = receive_response(client_socket)
                print("server:", response)
    except Exception as e:
        print(f"client: Error occurred: {e}")
    finally:
        close_socket(client_socket)

if __name__ == "__main__":
    main()