from flask.ext.socketio import emit
from .. import socketio
import datetime
from .. import config

# Is this right? Should we implement it all via an API?
if config.getboolean('as3935', 'attached'):
    from ..as3935 import sensor

date_format = config.get('interface', 'date_format')

@socketio.on('connect', namespace='/lightning_sensor')
def connected():
    timestamp = datetime.datetime.now().strftime(date_format)
    emit('sensor-interrupt',
        {
            'type': 'message',
            'message': 'Connected',
            'timestamp': timestamp,
        })

@socketio.on('adjust-setting', namespace='/lightning_sensor')
def adjust_setting(json):
    response = {'setting': json['setting']}
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
