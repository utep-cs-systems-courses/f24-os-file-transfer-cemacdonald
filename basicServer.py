#! usr/bin/env python3

import socket, os, sys, re, time

def receiver(connection, filename):
    folder = "transferred-files"
    os.makedirs(folder_name, exist_ok=True)

    file_path = os.path.join(folder, filename)

    if os.path.isfile(file_path):
        os.remove(file_path)
        os.mkfifo(file_path)
    else:
        os.mkfifo(file_path)
    
    with open(file_path, 'wb') as file:
        while True:
            data = connection.recv(1024)
            if not data or data == b'end of file':
                break
            file.write(data)

def ack(connection, ack_message):
    ack_message = ack_message.encode()
    connection.sendall(ack_message)

def main():
 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1',50000))
    server_socket.listen(1)
    host = '127.0.0.1'
    port = 50000
    print(f"Server is listening on {host}:{port}")

    connection, address = server_socket.accept()
    print(f"Connection from {address}")

    received_filename = connection.recv(1024).decode()
    print(f"Receiving file: {received_filename}")

    receive_file(connection, received_filename)
    print("File has been successfully received.")

    ack_message = "Successfully received. Acknowledgement sent"
    ack(connection, ack_message)
    print("Acknowledgement sent")

    connection.shutdown(socket.SHUT_WR)
    connection.close()
    server_socket.close()

if __name__ == "__main__":
    main()
