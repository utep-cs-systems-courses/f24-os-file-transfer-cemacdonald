#! /usr/bin/env python3
import socket
import os
import sys
import threading
from io import BufferedReader, FileIO

def outBandDeframe(files):
    extracted_files, extracted_contents = [], []
    
    if not os.path.exists(files):                              
        os.write(2, ("Framed file %s does not exist\n" % files).encode())
        exit()
    
    fdReader = os.open(files, os.O_RDONLY)                     
    read_file = BufferedReader(FileIO(fdReader))       

    while True:
        fname = read_file.readline().decode().rstrip()    

        if not fname:                                  
            break

        fname = f"{fname.split('.')[0]}2"
        fdWriter = os.open(fname, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o777)
        
        fsize_str = read_file.readline().decode().rstrip()
        if not fsize_str:
            break
        
        fsize = int(fsize_str)
        contents = read_file.read(fsize)
        os.write(fdWriter, contents)
        
        extracted_files.append(fname)
        extracted_contents.append(contents)

    os.close(fdReader)

    return extracted_files, extracted_contents

def receiver(connection):
    folder = "transferred-files"
    os.makedirs(folder, exist_ok=True)
    filename = connection.recv(1024).decode()
    file_path = os.path.join(folder, filename)

    if os.path.isfile(file_path):
        os.remove(file_path)
    os.mkfifo(file_path)

    framed_data = b""

    with open(file_path, 'wb') as file:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            file.write(data)
            framed_data += data
    
    extracted_files, extracted_contents = outBandDeframe(file_path)

    os.remove(file_path)

    return extracted_files, extracted_contents

def ack(connection, ack_message):
    ack_message = ack_message.encode()
    connection.sendall(ack_message)

def handle_client(connection, address):
    print(f"Connection from {address}")
    incoming = connection.recv(1024).decode()

    print(f"Receiving file: {incoming}")
    received_filename, received_contents = receiver(connection)

    if received_filename and received_contents:
        print("File has been successfully received.")

    ack_message = "Acknowledged"
    ack(connection, ack_message)

    print("Acknowledgement sent")

    connection.shutdown(socket.SHUT_WR)
    connection.close()

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 50000))
    sock.listen(5)
    
    print("Server is listening on 127.0.0.1:50000")

    while True:
        connection, address = sock.accept()
        thread = threading.Thread(target=handle_client, args=(connection, address))
        thread.start()
        thread.join()  # Wait for the thread to finish
    
    print("We are done for the day!")

if __name__ == "__main__":
    main()
