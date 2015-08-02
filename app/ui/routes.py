from flask import render_template, url_for, request
from . import ui
from .. import config

if config.getboolean('as3935', 'attached'):
    from ..as3935 import sensor

date_format = config.get('interface', 'date_format')

settings = dict()
settings['units'] = config.get('interface', 'units')
settings['attached'] = config.getboolean('as3935', 'attached')

if settings['attached']:
    settings['read_only'] = config.getboolean('interface', 'read_only')
    settings['editable_fields'] = ['disturber', 'noise-floor', 'min-strikes', 'indoors']
    settings['disturber'] = sensor.get_mask_disturber()
    settings['indoors'] = sensor.get_indoors()
    settings['min_strikes'] = sensor.get_min_strikes()
    settings['noise_floor'] = sensor.get_noise_floor()

@ui.route('/')
def index():
    if settings['attached']:
        settings['disturber'] = sensor.get_mask_disturber()
        settings['indoors'] = sensor.get_indoors()
        settings['min_strikes'] = sensor.get_min_strikes()
        settings['noise_floor'] = sensor.get_noise_floor()
    return render_template('index.html', settings=settings)
