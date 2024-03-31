#! /usr/bin/env python3

import socket, os, sys, re, time
from io import BufferedReader, FileIO

def outBandDeframe(files):
    extracted_files,extracted_contents = [], []
    #error handling
    if not os.path.exists(files):                              
        os.write(2,("Framed file %s does not exist\n" % files).encode())
        exit()
    #opening framed file for extraction
    fdReader = os.open(files, os.O_RDONLY)                     
    read_file = BufferedReader(FileIO(fdReader))       
    
    while True:
        #decode file
        fname = read_file.readline().decode().rstrip()    

        if not fname:                                  
            break
        #creates new file, 2.0 version of framed file
        fname = f"{fname.split('.')[0]}2"
        fdWriter = os.open(fname, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, stat.S_IRWXU)
        #error handling
        fsize_str  = read_file.readline().decode().rstrip()
        if not  fsize_str:
            break
        fsize = int(fsize_str)
        contents = read_file.read(fsize)
        os.write(fdWriter,contents)
        extracted_files.append(fname)
        extracted_contents.append(contents)

    tar_file.close()

    return extracted_files, extracted_contents


#processing client's file
def receiver(connection):
    folder = "transferred-files"
    os.makedirs(folder, exist_ok=True)
    filename = connection.recv(1024).decode()
    file_path = os.path.join(folder, filename)

    if os.path.isfile(file_path):
        os.remove(file_path)
        os.mkfifo(file_path)
    else:
        os.mkfifo(file_path)

    framed_data = b""

    with open(file_path,'wb') as file:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            file.write(data)
            framed_data += data
    extracted_files, extracted_contents = outBandDeframe(file_path)

    os.remove(file_path)

    return extracted_files, extracted_contents
    

#sends acknowledgement message to client
def ack(connection, ack_message):
    ack_message = ack_message.encode()
    connection.sendall(ack_message)

#runs all methods for file transfer
def main():
 
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1',50000))
    server_socket.listen(1)
    
    host = '127.0.0.1'
    port = 50000
    
    print(f"Server is listening on {host}:{port}")

    connection, address = server_socket.accept()
    print(f"Connection from {address}")

    incoming = connection.recv(1024).decode()

    print(f"Receiving file: {incoming}")

    received_filename,received_contents = receiver(connection)
    if received_filename and recieved_contents != None:
        print("File has been successfully received.")

    ack_message = "Acknowledged"
    ack(connection, ack_message)
    print("Acknowledgement sent")

    connection.shutdown(socket.SHUT_WR)
    connection.close()
    server_socket.close()

if __name__ == "__main__":
    main()
