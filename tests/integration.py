import datetime
import logging
import sys
from unittest.mock import MagicMock

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

if sys.platform != 'linux':
    bluepy_mock = MagicMock()
    p_mock = MagicMock()
    bluepy_mock.btle.Peripheral.return_value = p_mock

    sys.modules['bluepy'] = bluepy_mock
from lywsd02 import Lywsd02Client

mac = '3F:59:C8:80:70:BE'


def create_client():
    return Lywsd02Client(mac)


if __name__ == '__main__':
    client = create_client()
    dt = datetime.datetime.now()
    with client.connect():
        temperature = client.temperature
        humidity = client.humidity
        time = client.time

    print(temperature, humidity, time)
