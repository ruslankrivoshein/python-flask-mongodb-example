import pytest
from pytest_mock_resources import create_mongo_fixture

from src import api
from src.app import create_app

mongo = create_mongo_fixture()


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        'TESTING': True,
    })

    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def expected_error_message():
    return {
        'errors': [
            {
                'status': '418',
                'source': {
                    'pointer': '/stub_url',
                },
                'title': 'test',
                'detail': 'test',
            },
        ],
    }


@pytest.fixture()
def songs():
    return [
        {
            'artist': 'Artist 1',
            'title': 'Lycanthropic Metamorphosis',
            'difficulty': 14.6,
            'level': 13,
            'released': '2016-10-26',
        },
        {
            'artist': 'Artist 1',
            'title': 'A New Kennel',
            'difficulty': 9.1,
            'level': 9,
            'released': '2010-02-03',
        },
        {
            'artist': 'Artist 2',
            'title': 'Awaki-Waki',
            'difficulty': 15,
            'level': 13,
            'released': '2012-05-11',
        },
        {
            'artist': 'Artist 1',
            'title': 'You\'ve Got The Power',
            'difficulty': 13.22,
            'level': 13,
            'released': '2014-12-20',
        },
        {
            'artist': 'Artist 1',
            'title': 'Wishing In The Night',
            'difficulty': 10.98,
            'level': 9,
            'released': '2016-01-01',
        },
        {
            'artist': 'Artist 1',
            'title': 'Opa Opa',
            'difficulty': 14.66,
            'level': 13,
            'released': '2013-04-27',
        },
        {
            'artist': 'Artist 1',
            'title': 'Greasy Fingers - boss level',
            'difficulty': 2,
            'level': 3,
            'released': '2016-03-01',
        },
        {
            'artist': 'Artist 1',
            'title': 'Alabama Sunrise',
            'difficulty': 5,
            'level': 6,
            'released': '2016-04-01',
        },
        {
            'artist': 'Artist 1',
            'title': 'Can\'t Buy Me Skills',
            'difficulty': 9,
            'level': 9,
            'released': '2016-05-01',
        },
        {
            'artist': 'Artist 1',
            'title': 'Vivaldi Allegro Mashup',
            'difficulty': 13,
            'level': 13,
            'released': '2016-06-01',
        },
        {
            'artist': 'Artist 1',
            'title': 'Babysitting',
            'difficulty': 7,
            'level': 6,
            'released': '2016-07-01',
        },
    ]


@pytest.fixture()
def environment(monkeypatch, client, songs, mongo):
    def mock_mongo():
        return mongo

    monkeypatch.setattr(api, '_get_mongo_connection', mock_mongo)

    mongo.songs.insert_many(songs)
    mongo.songs.create_index([('artist', 'text'), ('title', 'text')])

    for song in songs:
        del song['_id']

    return client
