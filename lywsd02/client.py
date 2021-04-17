import collections
import contextlib
import logging
import struct
import time
from datetime import datetime

from bluepy import btle

_LOGGER = logging.getLogger(__name__)

UUID_UNITS = 'EBE0CCBE-7A0A-4B0C-8A1A-6FF2997DA3A6'        # 0x00 - F, 0x01 - C    READ WRITE
UUID_HISTORY = 'EBE0CCBC-7A0A-4B0C-8A1A-6FF2997DA3A6'      # Last idx 152          READ NOTIFY
UUID_TIME = 'EBE0CCB7-7A0A-4B0C-8A1A-6FF2997DA3A6'         # 5 or 4 bytes          READ WRITE
UUID_DATA = 'EBE0CCC1-7A0A-4B0C-8A1A-6FF2997DA3A6'         # 3 bytes               READ NOTIFY
UUID_BATTERY = 'EBE0CCC4-7A0A-4B0C-8A1A-6FF2997DA3A6'      # 1 byte                READ
UUID_NUM_RECORDS = 'EBE0CCB9-7A0A-4B0C-8A1A-6FF2997DA3A6'  # 8 bytes               READ
UUID_RECORD_IDX = 'EBE0CCBA-7A0A-4B0C-8A1A-6FF2997DA3A6'   # 4 bytes               READ WRITE


class SensorData(collections.namedtuple('SensorDataBase', ['temperature', 'humidity', 'voltage', 'batteryLevel'])):
    __slots__ = ()


class Lywsd02Client:
    UNITS = {
        b'\x01': 'F',
        b'\xff': 'C',
    }
    UNITS_CODES = {
        'C': b'\xff',
        'F': b'\x01',
    }

    def __init__(self, mac, notification_timeout=5.0):
        self._mac = mac
        self._peripheral = btle.Peripheral()
        self._notification_timeout = notification_timeout
        self._handles = {}
        self._tz_offset = None
        self._data = SensorData(None, None, None, None)
        self._history_data = collections.OrderedDict()
        self._context_depth = 0

    @contextlib.contextmanager
    def connect(self):
        if self._context_depth == 0:
            _LOGGER.debug('Connecting to %s', self._mac)
            self._peripheral.connect(self._mac)
        self._context_depth += 1
        try:
            yield self
        finally:
            self._context_depth -= 1
            if self._context_depth == 0:
                _LOGGER.debug('Disconnecting from %s', self._mac)
                self._peripheral.disconnect()

    @property
    def temperature(self):
        return self.data.temperature

    @property
    def humidity(self):
        return self.data.humidity

    @property
    def voltage(self):
        return self.data.voltage

    @property
    def batteryLevel(self):
        return self.data.batteryLevel

    @property
    def data(self):
        self._get_sensor_data()
        return self._data

    @property
    def units(self):
        with self.connect():
            ch = self._peripheral.getCharacteristics(uuid=UUID_UNITS)[0]
            value = ch.read()
        return self.UNITS[value]

    @units.setter
    def units(self, value):
        if value.upper() not in self.UNITS_CODES.keys():
            raise ValueError(
                'Units value must be one of %s' % self.UNITS_CODES.keys())

        with self.connect():
            ch = self._peripheral.getCharacteristics(uuid=UUID_UNITS)[0]
            ch.write(self.UNITS_CODES[value.upper()], withResponse=True)

    @property
    def battery(self):
        with self.connect():
            ch = self._peripheral.getCharacteristics(uuid=UUID_BATTERY)[0]
            value = ch.read()
        return ord(value)

    @property
    def time(self):
        with self.connect():
            ch = self._peripheral.getCharacteristics(uuid=UUID_TIME)[0]
            value = ch.read()
        if len(value) == 5:
            ts, tz_offset = struct.unpack('Ib', value)
        else:
            ts = struct.unpack('I', value)[0]
            tz_offset = 0
        return datetime.fromtimestamp(ts), tz_offset

    @time.setter
    def time(self, dt: datetime):
        data = struct.pack('Ib', int(dt.timestamp()), self.tz_offset)
        with self.connect():
            ch = self._peripheral.getCharacteristics(uuid=UUID_TIME)[0]
            ch.write(data, withResponse=True)

    @property
    def tz_offset(self):
        if self._tz_offset is not None:
            return self._tz_offset
        elif time.daylight:
            return -time.altzone // 3600
        else:
            return -time.timezone // 3600

    @tz_offset.setter
    def tz_offset(self, tz_offset: int):
        self._tz_offset = tz_offset

    @property
    def history_index(self):
        with self.connect():
            ch = self._peripheral.getCharacteristics(uuid=UUID_RECORD_IDX)[0]
            value = ch.read()
        _idx = 0 if len(value) == 0 else struct.unpack_from('I', value)
        return _idx

    @history_index.setter
    def history_index(self, value):
        with self.connect():
            ch = self._peripheral.getCharacteristics(uuid=UUID_RECORD_IDX)[0]
            ch.write(struct.pack('I', value), withResponse=True)

    @property
    def num_stored_entries(self):
        with self.connect():
            ch = self._peripheral.getCharacteristics(uuid=UUID_NUM_RECORDS)[0]
            value = ch.read()
        total_records, current_records = struct.unpack_from('II', value)
        return total_records, current_records

    @property
    def history_data(self):
        self._get_history_data()
        return self._history_data

    def _get_sensor_data(self):
        with self.connect():
            self._subscribe(UUID_DATA, self._process_sensor_data)

            if not self._peripheral.waitForNotifications(
                    self._notification_timeout):
                raise TimeoutError('No data from device for {} seconds'.format(
                    self._notification_timeout))

    def _get_history_data(self):
        with self.connect():
            self._subscribe(UUID_HISTORY, self._process_history_data)

            while True:
                if not self._peripheral.waitForNotifications(
                        self._notification_timeout):
                    break

    def handleNotification(self, handle, data):
        func = self._handles.get(handle)
        if func:
            func(data)

    def _subscribe(self, uuid, callback):
        self._peripheral.setDelegate(self)
        ch = self._peripheral.getCharacteristics(uuid=uuid)[0]
        self._handles[ch.getHandle()] = callback
        desc = ch.getDescriptors(forUUID=0x2902)[0]

        desc.write(0x01.to_bytes(2, byteorder="little"), withResponse=True)

    def _process_sensor_data(self, data):
        temperature, humidity, voltage = struct.unpack_from('<hBh', data)
        temperature /= 100
        voltage /= 1000

        batteryLevel = min(int(round((voltage - 2.1),2) * 100), 100)

        self._data = SensorData(temperature=temperature, humidity=humidity, voltage=voltage, batteryLevel=batteryLevel)

    def _process_history_data(self, data):
        (idx, ts, max_temp, max_hum, min_temp, min_hum) = struct.unpack_from('<IIhBhB', data)

        ts = datetime.fromtimestamp(ts)
        min_temp /= 100
        max_temp /= 100

        self._history_data[idx] = [ts, min_temp, min_hum, max_temp, max_hum]
