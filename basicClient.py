#! usr/bin/env python3

import sys,time,re,socket

#sends file to server
def sender(connection, file):
    with open(file, 'rb') as file:
        fr = file.read()
    connection.sendall(file.encode())
    time.sleep(1)
    connection.sendall(fr)
    time.sleep(1)
    connection.sendall(b'end of file')
#acknowledgement from server verification
def ack(connection):
    ack = connection.recv(1024).decode()
    print(f"Acknowledgment recieved: {ack}")
#executes processes and sends to correct server
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('127.0.0.1',50000))

    file = sys.argv[1]
    print("Client wants to send: {file}")
    sender(sock,file)
    print("Client sent file successfully")

    ack(sock)
    print("Client is tired of sending file, closing time!")
    sock.close()

if __name__ == "__main__":
    main()
