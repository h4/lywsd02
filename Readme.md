# Lywsd02 – Python library to work with Xiaomi Temperature and Humidifier sensor

[![PyPI version](https://badge.fury.io/py/lywsd02.svg)](https://pypi.org/project/lywsd02/)

**WORK IN PROGRESS**

## Usage

Instantiate client with Lywsd02 mac address

```python
from lywsd02 import Lywsd02Client

mac = '3F:59:C8:80:70:BE'
client = Lywsd02Client(mac)
```

Read data

```python
print(client.temperature)
print(client.humidity)
```

## Available properties

* `client.temperature` – Sensor's temperature data in Celsius degrees. Updates with timeout (See below)
* `client.humidity` – Sensor's humidity data in percent. Updates with timeout
* `client.units` – Current temperature units displayed on screen. Returns `'C'` for Celsius and `'F'` for Fahrenheit
* `client.time` – Current time and timezone offset. Returns as tuple of `datetime.datetime` and `int`
* `client.battery` – Sensor's battery level in percent (0 to 100).

## Available setters

* `client.units = 'C'` – Changes temperature units displayed on screen
* `client.time = datetime.datetime.now()` - Changes time. Changing timezone offset is not possible

## Configuration

Client may be initialized with additional kwargs.

* `notification_timeout` – timeout to wait for `temperature` and `humidity` requests. If sensor responds slower 
then timeout data would not updated. Default value is 5 second.
* `data_request_timeout` – `temperature` and `humidity` are cached for this period. Default value is 15 second.

```python
from lywsd02 import Lywsd02Client

mac = '3F:59:C8:80:70:BE'
client = Lywsd02Client(mac, notification_timeout=1.0, data_request_timeout=30.0)
```
