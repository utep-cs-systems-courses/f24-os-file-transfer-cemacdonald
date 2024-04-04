#! /usr/bin/env python3
import sys
import socket
import os

#frames file for delivery
def outBandFrame(files):
    framed_data = b""
    for file in files:
        if not os.path.exists(file):
            print(f"File {file} does not exist", file=os.fdopen(2, 'w'))
            return None
        
        with open(file, "rb") as f:
            contents = f.read()
        
        file_size = len(contents)
        file_header = f"{file}\n{file_size}\n".encode()

        framed_data += file_header + contents
    
    return framed_data


def sender(connection, files):
    framed_file = outBandFrame(files)
    if framed_file:
        connection.sendall(framed_file)
        connection.sendall(b'eof')

def ack(connection):
    ack = connection.recv(1024).decode()
    print(f"Acknowledgment received: {ack}")

def main():
    if len(sys.argv) < 2:
        print("There needs to be more files to transfer :0")
        return
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1', 50000))

    files = sys.argv[1:]
    print(f"Client wants to send: {files}")
    sender(sock, files)
    print("Client sent file successfully")

    ack(sock)
    print("Client is tired of sending file, closing time!")
    sock.close()

if __name__ == "__main__":
    main()
