import os

from dotenv import load_dotenv
from flask import Flask
from flask_pymongo import BSONObjectIdConverter

from src.api import api
from src.modules.db import init_db
from src.utils import check_jsonapi_headers


def create_app():
    dotenv_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        '.env.d/app.env',
    )

    load_dotenv(dotenv_path)

    app = Flask(__name__)

    app.config['DEBUG'] = os.getenv('APP_DEBUG')
    app.config['MONGO_URI'] = os.getenv('APP_MONGO_CONNECTION_URI')
    app.url_map.converters["ObjectId"] = BSONObjectIdConverter

    app.register_blueprint(api)

    @app.before_request
    def init():
        if error := check_jsonapi_headers():
            return error

        init_db()

    @app.after_request
    def add_jsonapi_headers(response):
        response.mimetype = 'application/vnd.api+json'

        return response

    return app
