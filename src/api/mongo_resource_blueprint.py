from flask import Blueprint
from flask_pymongo import BSONObjectIdConverter


class MongoResourceBlueprint(Blueprint):
    def __call__(self, *args, **kwargs):
        Blueprint.__call__(self, *args, **kwargs)

        self.add_app_url_map_converter(BSONObjectIdConverter, 'ObjectId')

    def add_app_url_map_converter(self, func, name=None):
        """
        Register a custom URL map converters, available application wide.

        :param name: the optional name of the filter, otherwise
                     the function name will be used.
        """

        def register_converter(state):
            state.app.url_map.converters[name or func.__name__] = func

        self.record_once(register_converter)
