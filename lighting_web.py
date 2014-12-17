import os
from flask import Flask, render_template
from flask.ext.socketio import SocketIO, emit
from RPi_AS3935 import RPi_AS3935
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
sensor = RPi_AS3935(address=0x00, bus=0)

sensor.set_indoors(True)
sensor.set_noise_floor(0)
sensor.calibrate(tun_cap=0x0F)

def register_strike(channel):
    time.sleep(0.004)
    global sensor
    reason = sensor.get_interrupt()
    if reason == 0x08:
        socketio.emit('lightning', 
                      { 'type': 'strike', 'distance': sensor.get_distance() },
                      namespace='/lightning_sensor'
                     )
    else:
        socketio.emit('lightning',
                      { 'type': 'fault' }, 
                      namespace='/lightning_sensor'
                     )

GPIO.setup(17, GPIO.IN)
GPIO.add_event_detect(17, GPIO.RISING, callback=register_strike)

app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'super secret key!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect', namespace='/lightning_sensor')
def connected():
    emit('lightning', { 'type': 'message', 'text': 'Connected to server.'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    if port == 5000:
        app.debug = True
    socketio.run(app, host='0.0.0.0', port=port)
