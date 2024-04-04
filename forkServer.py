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

    os.close()

    return extracted_files, extracted_contents


#processing client's file
def receiver(connection):
    #makes directory for new files
    
    folder = "transferred-files"
    os.makedirs(folder, exist_ok=True)
    filename = connection.recv(1024).decode()
    file_path = os.path.join(folder, filename)
    #error handling
    
    if os.path.isfile(file_path):
        os.remove(file_path)
    os.mkfifo(file_path)

    #gets framed data from client
    framed_data = b""
    
    with open(file_path,'wb') as file:
        while True:
            data = connection.recv(1024)
            if not data:
                break
            file.write(data)
            framed_data += data
    #deframes framed data from client
    extracted_files, extracted_contents = outBandDeframe(file_path)

    os.remove(file_path)

    return extracted_files, extracted_contents
    

#sends acknowledgement message to client
def ack(connection, ack_message):
    ack_message = ack_message.encode()
    connection.sendall(ack_message)
    
def reap_zombies():
    while True:
        try:
            # Reap child processes
            pid, status = os.waitpid(-1, os.WNOHANG)
            if pid == 0:
                break
            print(f"Child process {pid} terminated")
        except OSError:
            break

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 50000))
    sock.listen(5)  # Maximum 5 pending connections

    host = '127.0.0.1'
    port = 50000
    
    print(f"Server is listening on {host}:{port}")

    while True:
        reap_zombies()
        connection, address = sock.accept()
        print(f"Connection from {address}")

        # Fork a new process
        pid = os.fork()

        if pid == 0:  # Child process
            sock.close()  # Close server socket in child process
            
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
            sys.exit(0)  # Exit child process

        else:  # Parent process
            connection.close()  # Close connection socket in parent process

if __name__ == "__main__":
    main()
