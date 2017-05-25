def _find_server_error(response, err_code=None, msg_part=None):
    if err_code is None and msg_part is None:
        raise ValueError(
            'You must specify either error code or part of error message')

    data = response.data
    errors = data.get('errors', [])
    msg_part = msg_part.lower()

    for error in errors:
        err_code_matches = (err_code is None or error['code'] == err_code)
        msg_matches = (
            msg_part is None or msg_part in error['message'].lower())
        if err_code_matches or msg_matches:
            return True

    return False
