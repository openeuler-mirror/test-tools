import socket  

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  
server_socket.bind(('localhost', 12345))  
server_socket.listen(1)  
while True:  
    connection, _ = server_socket.accept()  
    while True:  
        data = connection.recv(1024)  
        if not data:  
            break  
        connection.sendall(data)
