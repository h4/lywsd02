# Lywsd02 – Python library to work with Xiaomi Temperature and Humidifier sensor

[![PyPI version](https://badge.fury.io/py/lywsd02.svg)](https://pypi.org/project/lywsd02/)

**WORK IN PROGRESS**

## Install

1. Install it via [PyPI](https://pypi.org/project/lywsd02/):

    ```
    pip install lywsd02
    ```

    Note: use `pip3` instead of `pip` on Raspbian and other systems that default to Python 2.

2. Or directly from the [source code](https://github.com/h4/lywsd02):

    ```
    git clone https://github.com/h4/lywsd02.git
    python lywsd02/setup.py install
    ```

    Note: use `python3` if your system defaults to Python 2.

## Usage

Instantiate client with Lywsd02 mac address

```python
from lywsd02 import Lywsd02Client

mac = '3F:59:C8:80:70:BE'
client = Lywsd02Client(mac)
```

Read data (each property will be fetched using new connection)

```python
print(client.temperature)
print(client.humidity)
```

Read temperature as humidity from a single notification

```python
data = client.data
print(data.temperature)
print(data.humidity)


Read data (all data will be retrieved with a single connection)

```python
with client.connect():
    data = client.data
    print(data.temperature)
    print(data.humidity)
    print(client.battery)
```

## Available properties

* `client.temperature` – Sensor's temperature data in Celsius degrees. Updates with timeout (See below)
* `client.humidity` – Sensor's humidity data in percent. Updates with timeout
* `client.units` – Current temperature units displayed on screen. Returns `'C'` for Celsius and `'F'` for Fahrenheit
* `client.time` – Current time and timezone offset. Returns as tuple of `datetime.datetime` and `int`
* `client.battery` – Sensor's battery level in percent (0 to 100).

## Available setters

* `client.units = 'C'` – Changes temperature units displayed on screen
* `client.time = datetime.datetime.now()` - Changes time using local timezone or tz_offset (if set)
* `client.tz_offset = 1` - Sets timezone offset in hours that will be used when setting time

## Configuration

Client may be initialized with additional kwargs.

* `notification_timeout` – timeout to wait for `temperature` and `humidity` requests. If sensor responds slower
then timeout data would not updated. Default value is 5 second.

```python
from lywsd02 import Lywsd02Client

mac = '3F:59:C8:80:70:BE'
client = Lywsd02Client(mac, notification_timeout=1.0, data_request_timeout=30.0)
```
