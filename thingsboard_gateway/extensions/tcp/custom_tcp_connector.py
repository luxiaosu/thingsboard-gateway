import socket
import struct

server_ip = '192.168.50.252'
server_port = 8000

#tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#tcp_client_socket.connect((server_ip, server_port))

tcp_client_socket = socket.create_connection((server_ip, server_port))

send_data = struct.pack('8B', int('01', 16), int('01', 16), int('00', 16), int('00', 16), int('00', 16), int('04', 16), int('3D', 16), int('C9', 16))
#tcp_client_socket.send(send_data)
send_data = 'test'
tcp_client_socket.sendall(send_data.encode())
recv_data = tcp_client_socket.recv(1024)
print(recv_data)

tcp_client_socket.close()
