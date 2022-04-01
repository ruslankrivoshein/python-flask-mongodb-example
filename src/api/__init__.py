import os
import urllib.parse
from math import ceil

import pymongo
from bson import ObjectId
from flask import g, make_response, request
from pydantic import ValidationError

from src.api.mongo_resource_blueprint import MongoResourceBlueprint
from src.models import BaseSong, Rating
from src.utils import build_jsonapi_error_message

api = MongoResourceBlueprint('api', __name__, url_prefix='/api')


def _get_mongo_connection():
    return g.db


@api.route('/songs/')
def get_songs():
    min_oid = ObjectId('0' * 24)
    max_oid = ObjectId('f' * 24)

    page_size = int(os.getenv('APP_PAGE_SIZE'))

    cursor, limit, sort_params = (
        request.args.get('page[cursor]', min_oid, type=ObjectId),
        request.args.get('page[size]', page_size, type=int),
        request.args.get('sort', '_id', type=str),
    )

    sort_params = sort_params.split(',')

    if '_id' in sort_params:
        cursor = max_oid if '_id'.startswith('-') else min_oid

    sort = []

    for field in sort_params:
        if field.startswith('-'):
            order = pymongo.DESCENDING
            _field = field[1:]
        else:
            order = pymongo.ASCENDING
            _field = field

        sort.append((_field, order))

    conn = _get_mongo_connection()

    songs = conn.songs.find({'_id': {'$gt': cursor}}).sort(sort).limit(limit)

    data = []

    for item in songs:
        song = BaseSong.parse_obj(item)

        data.append({
            'type': 'songs',
            'id': str(item['_id']),
            'attributes': song.dict(),
        })

    total_pages = ceil(conn.songs.count_documents({}) / limit)

    response = make_response({
        'meta': {
            'total_pages': total_pages,
        },
        'data': data,
        'links': {
            'next': '?'.join([
                f'{request.base_url}',
                urllib.parse.quote(
                    f'page[cursor]={data[-1]["id"]}&page[size]={limit}',
                ),
            ]),
        },
    })

    return response


@api.route('/songs/avg_difficulty/')
def get_avg_difficulty():
    level = request.args.get('level', {'$exists': True}, type=int)

    avg_field_name = 'avg_difficulty'

    conn = _get_mongo_connection()

    try:
        avg = next(
            conn.songs.aggregate(
                [
                    {
                        '$match': {
                            'level': level,
                        }
                    },
                    {
                        '$group': {
                            '_id': None,
                            avg_field_name: {
                                '$avg': '$difficulty',
                            },
                        },
                    },
                    {
                        '$project': {
                            # TODO: use $round when the testing library
                            #  will be supporting it
                            avg_field_name: f'${avg_field_name}',
                        },
                    },
                ],
            )
        )
    except StopIteration:
        avg = {}

    response = make_response({
        'data': {
            avg_field_name: round(avg.get(avg_field_name, 0), 3),
        }
    })

    return response


@api.route('/search/')
def search():
    message = request.args.get('message', None, type=str)

    conn = _get_mongo_connection()

    songs = conn.songs.find({'$text': {'$search': message}})

    data = []

    for item in songs:
        song = BaseSong.parse_obj(item)

        data.append({
            'type': 'songs',
            'id': str(item['_id']),
            'attributes': song.dict(),
        })

    response = make_response({
        'data': data,
    })

    return response


@api.route('/songs/<ObjectId:id>/rate/', methods=['POST'])
def rate_song(id):
    try:
        rating = request.json['data']['attributes']['value']
    except KeyError:
        return build_jsonapi_error_message(
            400,
            request.path,
            'Invalid request body',
            'Request body must follow JSON:API specification '
            'and contain data within `data[attributes]` object',
        ), 400

    try:
        rating = Rating(song_id=id, value=rating)
    except ValidationError:
        return build_jsonapi_error_message(
            400,
            request.path,
            'Invalid rating value',
            'Rating must be between 1 and 5',
        ), 400

    conn = _get_mongo_connection()

    row = conn.ratings.insert_one(rating.dict())

    response = make_response({
        'data': {
            'type': 'ratings',
            'id': str(row.inserted_id),
            'attributes': {
                'value': rating.value,
            }
        }
    })

    response.status_code = 201

    return response


@api.route('/songs/<ObjectId:song_id>/rating/')
def get_rating_by_song_id(song_id):
    conn = _get_mongo_connection()

    try:
        ratings = next(
            conn.ratings.aggregate(
                [
                    {
                        '$match': {
                            'song_id': song_id,
                        },
                    },
                    {
                        '$group': {
                            '_id': None,
                            'highest': {
                                '$max': '$value',
                            },
                            'average': {
                                '$avg': '$value',
                            },
                            'lowest': {
                                '$min': '$value',
                            },
                        },
                    },
                    {
                        '$project': {
                            'highest': '$highest',
                            'average': '$average',
                            'lowest': '$lowest',
                        },
                    },
                ],
            ),
        )
    except StopIteration:
        return '', 404

    response = make_response({
        'data': {
            'highest': ratings['highest'],
            'average': round(ratings['average']),
            'lowest': ratings['lowest'],
        }
    })

    return response
