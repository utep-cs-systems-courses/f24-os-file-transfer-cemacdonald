#! /usr/bin/env python3

import sys,time,re,socket


def outBandFrame(files):
    #error handling
    for file in files:
        if not os.path.exists(file):
            print(f"File {file} does not exist", file=os.fdopen(2, 'w'))
            return
        #opening file for encoding
        with open(file, "rb") as f:
            contents = f.read()
        #only framing header and size of file
        file_size = len(contents)
        file_header = f"{file}\n{file_size}\n".encode()

        os.write(1, file_header)
        os.write(1, contents)
#sends file to server
def sender(connection, file):
    with open(file, 'rb') as f:
        fr = f.read()
    framed_file = outBandFrame(file)
    connection.sendall(framed_file)
    connection.sendall(b'eof')
    
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
