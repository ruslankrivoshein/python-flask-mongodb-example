from src.utils import build_jsonapi_error_message, check_jsonapi_headers


def test_correct_error_message(expected_error_message):
    message = build_jsonapi_error_message(418, '/stub_url', 'test', 'test')

    assert expected_error_message == message
    assert 'errors' in message
    assert isinstance(message['errors'][0]['status'], str)
    assert (
        [
            'status', 'source', 'title', 'detail'
        ] == list(message['errors'][0].keys())
    )
    assert message['errors'][0]['source']['pointer'] == '/stub_url'


def test_returning_correct_get_response(environment, client, songs):
    response_list = client.get('/api/songs/').json

    assert {'data', 'links', 'meta'}.issubset(response_list.keys())
    assert 'attributes' in response_list['data'][0]


def test_correct_pagination(environment, client):
    response_base = client.get('/api/songs/').json
    assert response_base['meta']['total_pages'] == 3

    response_paginated_10 = client.get('/api/songs/?page[size]=10').json
    assert response_paginated_10['meta']['total_pages'] == 2

    response_paginated_100 = client.get('/api/songs/?page[size]=100').json
    assert response_paginated_100['meta']['total_pages'] == 1


def test_404_if_unexisting_level_passed(environment, client):
    response = client.get('/api/songs/avg_difficulty/?level=999').json

    assert response['data']['avg_difficulty'] == 0


def test_returning_common_difficulty_when_no_level_passed(environment, client):
    response = client.get('/api/songs/avg_difficulty/').json

    assert response['data']['avg_difficulty'] == 10.324


def test_search_is_case_insensitive(environment, client):
    response = client.get('/api/search/?message=opa').json

    assert response['data'][0]['attributes'] == {
        'artist': 'Artist 1',
        'difficulty': 14.66,
        'level': 13,
        'released': '2013-04-27',
        'title': 'Opa Opa'
    }


def test_required_headers_for_post(monkeypatch, app):
    context = {
        'headers': {
            'Content-Type': 'application/vnd.api+json',
            'Accept': 'application/vnd.api+json',
        },
        'method': 'POST',
        'path': 'stub_path',
    }

    with app.test_request_context(**context):
        assert check_jsonapi_headers() is None


def test_rate_returns_400_if_not_jsonapi_request(environment, client):
    response = client.post(
        '/api/songs/000000000000000000000000/rate/',
        headers={'Content-Type': 'application/vnd.api+json'},
        json={'rating': 1},
    )

    assert response.status_code == 400


def test_returning_correct_rating_by_song_id(environment, client):
    songs = client.get('/api/songs/').json

    song_id = songs['data'][0]['id']

    client.post(
        f'/api/songs/{song_id}/rate/',
        headers={'Content-Type': 'application/vnd.api+json'},
        json={'data': {'type': 'ratings', 'attributes': {'value': 1}}},
    )
    client.post(
        f'/api/songs/{song_id}/rate/',
        headers={'Content-Type': 'application/vnd.api+json'},
        json={'data': {'type': 'ratings', 'attributes': {'value': 2}}},
    )
    client.post(
        f'/api/songs/{song_id}/rate/',
        headers={'Content-Type': 'application/vnd.api+json'},
        json={'data': {'type': 'ratings', 'attributes': {'value': 3}}},
    )

    response = client.get(f'/api/songs/{song_id}/rating/')

    assert response.json == {'data': {'average': 2.0, 'highest': 3, 'lowest': 1}}


def test_returning_404_if_song_not_exists(environment, client):
    response = client.get('/api/songs/000000000000000000000000/rating/')

    assert response.status_code == 404
