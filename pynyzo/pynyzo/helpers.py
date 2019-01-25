"""
Helper Class and functions
"""

import logging


def base_app_log(app_log=None):
    """Returns the best possible log handler if none is provided"""
    if app_log:
        return app_log
    elif logging.getLogger("tornado.application"):
        return logging.getLogger("tornado.application")
    else:
        return logging
