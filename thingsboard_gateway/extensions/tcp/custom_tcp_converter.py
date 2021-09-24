from build.lib.thingsboard_gateway.connectors import converter
from thingsboard_gateway.connectors.converter import Converter, log

class CustomTcpUplinkConverter(Converter):
    def __ini__(self, config):
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
            try:
                