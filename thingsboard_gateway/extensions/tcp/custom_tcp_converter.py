from thingsboard_gateway.connectors.converter import Converter, log
import struct
class CustomTcpUplinkConverter(Converter):
    def __init__(self, config):
        self.__config = config
        self.__result = {
            "deviceName": config.get("deviceName", "CustomTcpDevice"),
            "deviceType": config.get("deviceType", "default"),
            "attributes": [],
            "telemetry": []
        }

    def convert(self, config, data: bytes):
        keys = ["attributes", "telemetry"]
        for key in keys:
            self.__result[key] = []
            if self.__config.get(key) is not None:
                for config_object in self.__config.get(key):
                    if config_object["functionCode"] == 3:
                        data_to_convert = data[2 + config_object["address"] : 2 + config_object["address"] * 4]
                        converted_data = {config_object["key"]: struct.unpack('>f', data_to_convert)}
                        self.__result[key].append(converted_data)
        log.debug("Converted data: %s", self.__result)
        return self.__result                
