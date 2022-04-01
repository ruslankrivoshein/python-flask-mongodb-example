from flask import make_response, request


def build_jsonapi_error_message(status_code, source, title, detail) -> dict:
    """https://jsonapi.org/format/#errors"""
    return {
        'errors': [
            {
                'status': str(status_code),
                'source': {
                    'pointer': source,
                },
                'title': title,
                'detail': detail,
            },
        ],
    }


def check_jsonapi_headers(*args, **kwargs):
    """Check headers according to JSON:API specification
    https://jsonapi.org/
    """
    ct_header = request.headers.get('Content-Type')

    if request.method in ('POST', 'PATCH'):
        if ('Content-Type' not in request.headers or
                'application/vnd.api+json' not in ct_header or
                ct_header != 'application/vnd.api+json'):
            status_code = 415

            error = build_jsonapi_error_message(
                status_code,
                request.path,
                'Invalid request header',
                'Content-Type header must be application/vnd.api+json',
            )

            return make_response(
                error, 415, {'Content-Type': 'application/vnd.api+json'},
            )

    if 'Accept' in request.headers:
        is_error = False

        for accept in request.headers['Accept'].split(','):
            if accept.strip() == 'application/vnd.api+json':
                is_error = False
                break

            if ('application/vnd.api+json' in accept and
                    accept.strip() != 'application/vnd.api+json'):
                is_error = True

        if is_error:
            status_code = 406

            error = build_jsonapi_error_message(
                status_code,
                request.path,
                'Invalid request header',
                detail='Accept header must be '
                       'application/vnd.api+json without '
                       'media type parameters',
            )

            return make_response(
                error, status_code,
                {'Content-Type': 'application/vnd.api+json'},
            )
