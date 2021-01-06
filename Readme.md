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

## Usage (library)

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
```

Read data (all data will be retrieved with a single connection)

```python
with client.connect():
    data = client.data
    print(data.temperature)
    print(data.humidity)
    print(client.battery)
```

Read the 10 most recent entries only

```python
with client.connect():
    total_records, current_records = client.num_stored_entries
    client.history_index = total_records - 10 + 1
    data = client.history_data
```


## Usage (helper script)

This library also installs a simple command-line utility called `lywsd02`.

It allows to synchronize time and read data from devices:

```bash
lywsd02 sync 3F:59:C8:80:70:BE
lywsd02 read 3F:59:C8:80:70:BE 3F:59:C8:80:70:BF
```

Consult `lywsd02 -h` to get information on all possible actions.

Note that you may need to replace `lywsd02` with `~/.local/bin/lywsd02` or some other path, depending on your installation settings.

## Available properties

* `client.temperature` – Sensor's temperature data in Celsius degrees. Updates with timeout (See below)
* `client.humidity` – Sensor's humidity data in percent. Updates with timeout
* `client.units` – Current temperature units displayed on screen. Returns `'C'` for Celsius and `'F'` for Fahrenheit
* `client.time` – Current time and timezone offset. Returns as tuple of `datetime.datetime` and `int`
* `client.battery` – Sensor's battery level in percent (0 to 100).
* `client.history_data` – Ordered Dictionary of hourly minimum and maximum including timestamp for temperature and humidity
* `client.num_stored_entries` - A tuple describing the `history_data` property. It holds the number of total records saved and currently stored records 
* `client.history_index` - Index where the `history_data` collection should be read from 

## Available setters

* `client.units = 'C'` – Changes temperature units displayed on screen
* `client.time = datetime.datetime.now()` - Changes time using local timezone or tz_offset (if set)
* `client.tz_offset = 1` - Sets timezone offset in hours that will be used when setting time
* `client.history_index = total_records - 9` - Sets an index so that `history_data` will be updated with the ten most recent entries

## Configuration

Client may be initialized with additional kwargs.

* `notification_timeout` – timeout to wait for `temperature` and `humidity` requests. If sensor responds slower
then timeout data would not updated. Default value is 5 second.

```python
from lywsd02 import Lywsd02Client

mac = '3F:59:C8:80:70:BE'
client = Lywsd02Client(mac, notification_timeout=1.0, data_request_timeout=30.0)
```

## Troubleshooting

### Can't install the package form pip

Error:

```
ERROR: Command errored out with exit status 1: /usr/bin/python3 -u -c 'import sys, setuptools, tokenize; sys.argv[0] = '"'"'/tmp/pip-install-m1_xzdf5/bluepy/setup.py'"'"'; __file__='"'"'/tmp/pip-install-m1_xzdf5/bluepy/setup.py'"'"';f=getattr(tokenize, '"'"'open'"'"', open)(__file__);code=f.read().replace('"'"'\r\n'"'"', '"'"'\n'"'"');f.close();exec(compile(code, __file__, '"'"'exec'"'"'))' install --record /tmp/pip-record-00nadffm/install-record.txt --single-version-externally-managed --compile Check the logs for full command output.
```

Fix: Install glib2 library

```shell
# On RedHat/CentOS/Fedora:
dnf install glib2-devel

# On Ubuntu/Debian:
apt install libglib2.0-dev

# On Alpine:
apk add glib-dev
```
