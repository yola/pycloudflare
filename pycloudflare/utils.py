from pycloudflare.exceptions import SSLUnavailable
from pycloudflare.services import HTTPServiceError


errors_mapping = {
    1001: SSLUnavailable,
}


def translate_errors(f):
    def _wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except HTTPServiceError as exc:
            _translate_error(exc)

    return _wrapper


def _translate_error(exc):
    data = exc.response.data
    errors = data.get('errors', [])

    for error in errors:
        err_code = error['code']
        if err_code in errors_mapping:
            raise errors_mapping[err_code]()

    raise exc
