from functools import wraps

from pycloudflare.services import HTTPServiceError


def translate_errors(err_code, exc_class):
    def _translate_errors(f):
        @wraps(f)
        def _wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except HTTPServiceError as exc:
                _translate_error(exc, err_code, exc_class)

        return _wrapper

    return _translate_errors


def _translate_error(exc, err_code, exc_class):
    try:
        data = exc.response.json()
    except ValueError:
        # If response is not JSON, this error is not translatable.
        raise exc

    errors = data.get('errors', [])

    for error in errors:
        if error['code'] == err_code:
            raise exc_class()

    raise exc
