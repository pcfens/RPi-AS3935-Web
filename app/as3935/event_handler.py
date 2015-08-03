from . import sensor
import datetime
import time
from .. import config
import requests
from .. import socketio     # Remove this line after using the API

if config.getboolean('as3935', 'attached'):
    from ..as3935 import sensor

date_format = config.get('interface', 'date_format')
remote_endpoints = config.get('interface', 'remote_endpoints').split()

def register_strike(channel):
    timestamp = datetime.datetime.now().strftime(date_format)
    time.sleep(0.004)

    reason = sensor.get_interrupt()

    if reason == 0x08:
        data = {
            'type': 'strike',
            'distance': sensor.get_distance(),
            'timestamp': timestamp,
        }

    elif reason == 0x04:
        data = {
            'type': 'disturber',
            'message': 'Disturber',
            'timestamp': timestamp,
        }

    elif reason == 0x01:
        data = {
            'type': 'noise',
            'message': 'Noise',
            'timestamp': timestamp,
        }

    for remote in remote_endpoints:
        try:
            r = requests.post(remote, data=data)

        except Exception:
            pass
