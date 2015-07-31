from flask.ext.socketio import SocketIO
from flask import Flask
import ConfigParser

app = Flask(__name__)
socketio = SocketIO()

config = ConfigParser.RawConfigParser()
config.read('settings.cfg')

if config.getboolean('as3935', 'attached'):
    import as3935

from .main import main as main_blueprint
from .api import api_bp as api_blueprint

app.register_blueprint(main_blueprint)
app.register_blueprint(api_blueprint)

app.debug = config.getboolean('interface', 'debug_mode')

app.secret_key = 'SuperSecret'

socketio.init_app(app)
