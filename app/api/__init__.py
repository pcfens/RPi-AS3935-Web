from flask import Blueprint
from flask_restful import Api

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(api_bp)

import event_list
