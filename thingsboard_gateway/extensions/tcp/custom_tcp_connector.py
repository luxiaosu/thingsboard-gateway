from random import choice
from string import ascii_lowercase
from threading import Thread
from queue import Queue

import socket
import struct
import threading
import time
import types
from typing import Type
from thingsboard_gateway.connectors.connector import Connector, log
from thingsboard_gateway.tb_utility.tb_loader import TBModuleLoader

"""
server_ip = "192.168.88.4"
server_port = 8000

tcp_client_socket = socket.create_connection((server_ip, server_port))

send_data = struct.pack("8B", int("01", 16), int("01", 16), int("00", 16), int(
    "00", 16), int("00", 16), int("04", 16), int("3D", 16), int("C9", 16))
tcp_client_socket.sendall(send_data)

recv_data = tcp_client_socket.recv(1024)
print(recv_data.hex())

send_data = struct.pack("8B", int("01", 16), int("03", 16), int("00", 16), int(
    "00", 16), int("00", 16), int("04", 16), int("44", 16), int("09", 16))
tcp_client_socket.send(send_data)

recv_data = tcp_client_socket.recv(1024)
print(recv_data.hex())

tcp_client_socket.close()
"""
class CustomTcpConnector(Thread, Connector):
    def __init__(self, gateway, config, connector_type):
        super().__init__()
        self.statistics = {
            "MessagesReceived": 0,
            "MessagesSent": 0
        }
        self.__config = config
        self.__gateway = gateway
        self.setName(self.__config.get("name", "Custom %s connector" % self.get_name() + ''.join(choice(ascii_lowercase) for _ in  range(5))))
        log.info("Starting Custom %s connector", self.get_name())
        self.daemon = True
        self.stopped = True
        self.__connected = False
        self.__devices = {}
        self.__load_converters(connector_type)
        self.__connect_to_devices()
        self.__data_to_convert_queue = Queue()
        log.info("Custom connector %s initialization success.", self.get_name())
        log.info("Devices in configuration file found: %s", '\n'.join(device for device in self.__devices))

    def __load_converters(self, connector_type):
        devices_config = self.__config.get("devices")
        try:
            if devices_config is not None:
                for device_config in devices_config:
                    if device_config.get("converter") is not None:
                        converter = TBModuleLoader.import_module(connector_type, device_config["converter"])
                        self.__devices[device_config["deviceName"]] = {"converter": converter(device_config), "device_config": device_config}
                    else:
                        log.error("Converter configuration for the custom connector %s -- not found, please check your configuration file.", self.get_name())
            else:
                log.error("Section 'devices' in the configuration not found. A custom connector %s has being stopped.", self.get_name())
                self.close()
        except Exception as e:
            log.exception(e)
    
    def __connect_to_devices(self):
        for device in self.__devices:
            try:
                connection_start = time.time()
                server_ip = self.__devices[device]["device_config"]["host"]
                server_port = self.__devices[device]["device_config"]["port"]
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                # TCP connect keep alive
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                # idle = 60s(default = 7200s)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 60)
                # intvl = 5s (default = 75s)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 5)
                # cnt = 2 (default = 9)
                sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 2)
                self.__devices[device]["socket"] = sock.connect((server_ip, server_port))
            except Exception as e:
                log.exception(e)

    def run(self):
        #thread = threading.Thread(target=self.__poll_telemetry, args=(), daemon=True)
        #thread.start()
        try:
            while True:
                for device in self.__devices:
                    tcp_client_socket = self.__devices[device]["socket"]
                    
                    time.sleep(5)
        except Exception as e:
            log.exception(e)

    def open(self):
        self.stopped = False
        self.start()

    def close(self):
        self.stopped = True
        for device in self.__devices:
            self.__gateway.del_device(self.__devices[device])
            self.__devices[device]["socket"].close()

    def get_name(self):
        return self.name

    def is_connected(self):
        return self.__connected

    def on_attributes_update(self, content):
        pass

    def server_side_rpc_handler(self, content):
        pass
    
    def __convert_and_save_data(self, device, socket):
        while True:
            try:
                recv_data = socket.recv(1024)
                converted_data = self.__devices[device]["converter"].convert(self.__devices[device]["device_config"], recv_data)
                self.__gateway.send_to_storage(self.get_name(), converted_data)
            except Exception as e:
                log.exception(e)

    def __poll_telemetry(self, device, socket):
        while True:
            try:
                send_data = struct.pack("8B", int("01", 16), int("01", 16), int("00", 16), int(
                    "00", 16), int("00", 16), int("04", 16), int("3D", 16), int("C9", 16))
                socket.sendall(send_data)
            except Exception as e:
                log.exception(e)
