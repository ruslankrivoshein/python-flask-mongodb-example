from flask import g, current_app
from flask_pymongo import PyMongo


def init_db():
    if 'db' not in g:
        g.db = PyMongo(current_app, maxPoolSize=200).db

    return g.db
