import json


def get_config():
    """
    Return credentials.

    Either monkey patch this, or write a configuration file for it to read.
    """
    # Yola's internal configuration system:
    try:
        from yoconfig import get_config
        return get_config('cloudflare')
    except ImportError:
        pass

    with open('configuration.json') as f:
        return json.load(f)['common']['cloudflare']
