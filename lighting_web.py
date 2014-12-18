import os
from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
from RPi_AS3935 import RPi_AS3935
import RPi.GPIO as GPIO
import time, datetime

GPIO.setmode(GPIO.BCM)

tun_cap = 0x0F
bus = 0
date_format = '%H:%M:%S'
sensor_address = 0x00

# Rev. 1 Raspberry Pis should leave bus set at 0, while rev. 2 Pis should set
# bus equal to 1. The address should be changed to match the address of the
# sensor. (Common implementations are in README.md)
sensor = RPi_AS3935(address=sensor_address, bus=bus)

sensor.set_indoors(True)
sensor.set_noise_floor(0)
sensor.calibrate(tun_cap=tun_cap)

def register_strike(channel):
    timestamp = datetime.datetime.now().strftime(date_format)
    time.sleep(0.004)
    global sensor
    reason = sensor.get_interrupt()
    if reason == 0x08:
        socketio.emit('lightning', 
                      { 
                        'type': 'strike',
                        'distance': sensor.get_distance(),
                        'timestamp': timestamp,
                      },
                      namespace='/lightning_sensor'
                     )
    elif reason == 0x04:
        socketio.emit('lightning',
                      { 
                        'type': 'disturber',
                        'timestamp': timestamp,
                      },
                      namespace='/lightning_sensor'
                     )
    elif reason == 0x01:
        socketio.emit('lightning',
                      { 
                        'type': 'noise',
                        'timestamp': timestamp,
                      },
                      namespace='/lightning_sensor'
                     )

GPIO.setup(17, GPIO.IN)
GPIO.add_event_detect(17, GPIO.RISING, callback=register_strike)

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'super secret key!'
socketio = SocketIO(app)

@app.route('/')
def index():
    settings = dict()
    settings['disturber'] = sensor.get_mask_disturber()
    settings['indoors'] = sensor.get_indoors()
    settings['min_strikes'] = sensor.get_min_strikes()
    settings['noise_floor'] = sensor.get_noise_floor()
    return render_template('index.html', settings=settings)

@socketio.on('connect', namespace='/lightning_sensor')
def connected():
    timestamp = datetime.datetime.now().strftime(date_format)
    emit('lightning', 
            {
                'type': 'message', 
                'text': 'Connected',
                'timestamp': timestamp,
            })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if port == 5000:
        app.debug = True
    socketio.run(app, host='0.0.0.0', port=port)
