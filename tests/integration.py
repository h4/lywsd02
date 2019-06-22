import datetime

from lywsd02 import Lywsd02Client

mac = '3F:59:C8:80:70:BE'

client = Lywsd02Client(mac)

if __name__ == '__main__':
    dt = datetime.datetime.now()
    client.time = dt
