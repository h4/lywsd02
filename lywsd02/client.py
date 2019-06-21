import logging
import struct

from bluepy import btle

_LOGGER = logging.getLogger(__name__)

UUID_UNITS = 'EBE0CCBE-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 0x00 - F, 0x01 - C
UUID_HISTORY = 'EBE0CCBC-7A0A-4B0C-8A1A-6FF2997DA3A6'  # Last idx 152
UUID_CLOCK = 'EBE0CCB7-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 5 Bytes
UUID_DATA = 'EBE0CCC1-7A0A-4B0C-8A1A-6FF2997DA3A6'


class Lywsd02Client:
    def __init__(self, mac):
        self._mac = mac
        self._periferial = btle.Peripheral()
        self._temperature = None
        self._humidity = None

    @staticmethod
    def parse_humidity(value):
        return int(value)

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = struct.unpack('H', value)[0] / 100

    @property
    def humidity(self):
        return self._humidity

    @humidity.setter
    def humidity(self, value):
        self._humidity = value

    def handleNotification(self, cHandle, data):
        _LOGGER.info('BLE Data:')
        _LOGGER.info(data)

        temp_bytes = data[:2]
        humid_bytes = data[2]

        self.temperature = temp_bytes
        self.humidity = humid_bytes

    def get_data(self):
        _LOGGER.info('Trying to get new data')
        self._periferial.connect(self._mac)
        self._periferial.setDelegate(self)
        ch = self._periferial.getCharacteristics(uuid=UUID_DATA)[0]
        desc = ch.getDescriptors(forUUID=0x2902)[0]

        desc.write(0x01.to_bytes(2, byteorder="little"), withResponse=True)

        while True:
            _LOGGER.info("LOOP")
            if self._periferial.waitForNotifications(15.0):
                break

        self._periferial.disconnect()

        _LOGGER.info(self.humidity)

        return {
            'data': {
                'temperature': self.temperature,
                'humidity': self.humidity,
            }
        }
