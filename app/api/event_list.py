from flask_restful import reqparse, Resource, Api, fields, marshal, abort
from flask.ext.socketio import emit
from .. import socketio
from .. import config
from . import api
import datetime

date_format = config.get('interface', 'date_format')

parser = reqparse.RequestParser()
parser.add_argument('event')
parser.add_argument('distance', type=int)

events = []

class EventListAPI(Resource):
    def post(self):
        timestamp = datetime.datetime.now().strftime(date_format)
        args = parser.parse_args()
        obj = {'event': args['event'], 'distance': args['distance']}
        if args['event'] == 'strike':
            message = args['distance']
        elif args['event'] == 'disturber':
            message = 'Disturber'
        elif args['event'] == 'noise':
            message = 'Noise'
        else:
            message = args['event']
        data = {
            'type': args['event'],
            'message': message,
            'distance': args['distance'],
            'timestamp': timestamp,
        }

        # This needs to be stored somewhere better (like a real database)
        events.append(obj)

        socketio.emit('sensor-interrupt', data, namespace='/lightning_sensor')
        return obj, 201
    def get(self):
        return events

api.add_resource(EventListAPI, '/events')
