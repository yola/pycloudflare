class SSLUnavailable(Exception):
    """If you haven't verified a CNAME zone within the grace period (a week),
    it can't be verified any more.
    """
    pass
