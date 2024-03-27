#! usr/bin/env python3

import sys,time,re,socket

def encode(connection, file):
    with open(file, 'rb') as file:
        fr = file.read()
    connection.sendall(file.encode())
    time.sleep(1)
    connection.sendall(fr)
    time.sleep(1)
    connection.sendall(b'end of file')
def decode(connection):
    ack = connection.recv(1024).decode()
    print(f"Acknowledgment recieved: {ack}")
def main():
    host = '127.0.0.1'
    port = 50000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host,port))

    file = sys.argv[1]
    print("Client wants to send: {file}")
    encode(sock,file)
    print("Client sent file successfully")

    decode(sock)
    print("Client is tired of sending file, closing time!")
    sock.close()

if __name__ == "__main__":
    main()
