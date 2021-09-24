from threading import Thread

import socket
import struct

from thingsboard_gateway.connectors.connector import Connector, log

server_ip = "192.168.88.4"
server_port = 8000

tcp_client_socket = socket.create_connection((server_ip, server_port))

send_data = struct.pack("8B", int("01", 16), int("01", 16), int("00", 16), int(
    "00", 16), int("00", 16), int("04", 16), int("3D", 16), int("C9", 16))
tcp_client_socket.send(send_data)

recv_data = tcp_client_socket.recv(1024)
print(recv_data.hex())

send_data = struct.pack("8B", int("01", 16), int("03", 16), int("00", 16), int(
    "00", 16), int("00", 16), int("04", 16), int("44", 16), int("09", 16))
tcp_client_socket.send(send_data)

recv_data = tcp_client_socket.recv(1024)
print(recv_data.hex())

tcp_client_socket.close()


class CustomTcpConnector(Thread, Connector):
    def __init__(self, gateway, config, connetor_type):
        super().__init__()
        self.statistics = {
            "MessagesReceived": 0,
            "MessagesSent": 0
        }
        self.__config = config
        self.__gateway = gateway

