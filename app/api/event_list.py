from flask_restful import reqparse, Resource, Api, fields, marshal, abort
from flask.ext.socketio import emit
from .. import socketio
from .. import config
from . import api
import datetime

parser = reqparse.RequestParser()
parser.add_argument('type')
parser.add_argument('message')
parser.add_argument('timestamp')
parser.add_argument('distance', type=int)

events = []

class EventListAPI(Resource):
    def post(self):
        args = parser.parse_args()
        obj = {
            'type': args['type'],
            'message': args['message'],
            'distance': args['distance'],
            'timestamp': args['timestamp'],
        }

        # This needs to be stored somewhere better (like a real database)
        events.append(obj)

        socketio.emit('sensor-interrupt', obj, namespace='/lightning_sensor')
        return obj, 201
    def get(self):
        return events

api.add_resource(EventListAPI, '/events')
