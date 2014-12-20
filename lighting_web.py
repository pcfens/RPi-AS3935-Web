import os
from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
from RPi_AS3935 import RPi_AS3935
import RPi.GPIO as GPIO
import time, datetime
import ConfigParser

GPIO.setmode(GPIO.BCM)

config = ConfigParser.RawConfigParser()
config.read('settings.cfg')

editable_fields = ['disturber', 'noise-floor', 'min-strikes', 'indoors']

date_format = config.get('interface', 'date_format')

sensor = RPi_AS3935( address=int(config.get('as3935', 'address'), 0), bus=config.getint('pi', 'bus') )

sensor.calibrate(tun_cap=int(config.get('as3935', 'tuning_cap'), 0) )

event_history = list()

def register_strike(channel):
    timestamp = datetime.datetime.now().strftime(date_format)
    time.sleep(0.004)

    global sensor, event_history
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

    try:
        event_history.append(data)
        event_history = event_history[-5:]

        socketio.emit('sensor-interrupt',
                      data,
                      namespace='/lightning_sensor'
                     )
    except Exception:
        pass

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
    settings['read_only'] = config.getboolean('interface', 'read_only')
    settings['editable_fields'] = editable_fields

    return render_template('index.html', settings=settings)

@socketio.on('connect', namespace='/lightning_sensor')
def connected():
    timestamp = datetime.datetime.now().strftime(date_format)
    for event in event_history:
        emit('lightning', event)

    emit('sensor-interrupt', 
            {
                'type': 'message', 
                'message': 'Connected',
                'timestamp': timestamp,
            })

@socketio.on('adjust-setting', namespace='/lightning_sensor')
def adjust_setting(json):
    response = { 'setting': json['setting'] }
    if config.getboolean('interface', 'read_only'):
        pass
    else:
        if json['setting'] == 'disturber':
            disturber = not sensor.get_mask_disturber()
            sensor.set_mask_disturber(disturber)
            response['state'] = 'Masked' if disturber else 'Unmasked'

        elif json['setting'] == 'indoors':
            indoors = not sensor.get_indoors()
            sensor.set_indoors(indoors)
            response['state'] = 'Indoors' if indoors else 'Outdoors'

        elif json['setting'] == 'noise-floor':
            noise_floor = sensor.get_noise_floor()
            noise_floor = (noise_floor + 1) % 8
            sensor.set_noise_floor(noise_floor)
            response['state'] = sensor.get_noise_floor()

        elif json['setting'] == 'min-strikes':
            min_strikes = sensor.get_min_strikes()
            if min_strikes == 1:
                sensor.set_min_strikes(5)
            elif min_strikes == 5:
                sensor.set_min_strikes(9)
            elif min_strikes == 9:
                sensor.set_min_strikes(16)
            elif min_strikes == 16:
                sensor.set_min_strikes(1)

            response['state'] = sensor.get_min_strikes()

        emit('adjust-setting', response, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if port == 5000:
        app.debug = True
    socketio.run(app, host='0.0.0.0', port=port)
