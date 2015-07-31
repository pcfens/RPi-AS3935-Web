from RPi_AS3935 import RPi_AS3935
import RPi.GPIO as GPIO
from .. import config

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)
sensor = RPi_AS3935(address=int(config.get('as3935', 'address'), 0), bus=config.getint('pi', 'bus'))

from event_handler import register_strike
GPIO.add_event_detect(17, GPIO.RISING, callback=register_strike)

sensor.calibrate(tun_cap=int(config.get('as3935', 'tuning_cap'), 0))
