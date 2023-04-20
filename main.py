from dotenv import load_dotenv, find_dotenv

# from settings import app_config

load_dotenv(find_dotenv(), override=True)
mode = "SERVER"

import os
import sys
from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
import yaml
from dotenv import load_dotenv

from system.model_base import Session
from system.exceptions import register_error_handlers
from system.model_encoder import AlchemyEncoder
from system.flask_url_processor import RegexConverter
from system.mqtt_setup import mqtt_client
import paho.mqtt.client as mqtt
from env_config import get_config_docker


# CONFIG_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "config.yml")
sys.setrecursionlimit(1500)
load_dotenv()

def load_yaml_config(filename):
    with open(filename) as f:
        config = yaml.load(f)
    return config


def create_app(environment='dev'):

    app = Flask(__name__)
    CORS(app, expose_headers=["X-Total-Count"])
    app.url_map.strict_slashes = False
    app.url_map.converters['regex'] = RegexConverter
    app.json_encoder = AlchemyEncoder
    register_error_handlers(app)
    app.mode = mode

    # app.config.update(load_yaml_config(CONFIG_FILE))
    # app.config.from_object(app_config[environment])
    app.config['SQLALCHEMY_DATABASE_URI'] = get_config_docker("SQLALCHEMY_DATABASE_URI")

    app.sess = Session

    VERNEMQ_URL = os.getenv("VERNEMQ_URL")
    mqtt_client.connect(VERNEMQ_URL, 1883)
    app.mqtt_client = mqtt_client
    mqtt_client.loop_start()

    with app.app_context():
        from api.user import bp as api_user
        from api.farm import bp as api_farm
        from api.pond import bp as api_pond
        from api.device import bp as api_device

        app.register_blueprint(api_user)
        app.register_blueprint(api_farm)
        app.register_blueprint(api_pond)
        app.register_blueprint(api_device)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        Session.remove()

    return app


if __name__ == "__main__":
    lapp = create_app()
    lapp.run(host="0.0.0.0", debug=os.getenv("FLASK_DEBUG", False), port=5000)
