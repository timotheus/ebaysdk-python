# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

import platform
import logging

__version__ = '1.0.3'
Version = __version__  # for backware compatibility


UserAgent = 'eBaySDK/%s Python/%s %s/%s' % (
    __version__,
    platform.python_version(),
    platform.system(),
    platform.release()
)

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

log = logging.getLogger('ebaysdk')
perflog = logging.getLogger('ebaysdk.perf')

log.addHandler(NullHandler())
perflog.addHandler(NullHandler())

def get_version():
    return __version__

def set_file_logger(name, filepath, level=logging.INFO, format_string=None):
    global log
    log.handlers=[]

    if not format_string:
        format_string = "%(asctime)s %(name)s [%(levelname)s]:%(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.FileHandler(filepath)
    fh.setLevel(level)
    formatter = logging.Formatter(format_string)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    log = logger


def set_stream_logger(name, level=logging.DEBUG, format_string=None):
    global log
    log.handlers=[]

    if not format_string:
        format_string = "%(asctime)s %(name)s [%(levelname)s]:%(message)s"
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fh = logging.StreamHandler()
    fh.setLevel(level)
    formatter = logging.Formatter(format_string)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    log = logger

def trading(*args, **kwargs):
    from ebaysdk.trading import Connection as Trading
    return Trading(*args, **kwargs)

def shopping(*args, **kwargs):
    from ebaysdk.shopping import Connection as Shopping
    return Shopping(*args, **kwargs)

def finding(*args, **kwargs):
    from ebaysdk.finding import Connection as Finding
    return Finding(*args, **kwargs)

def merchandising(*args, **kwargs):
    from ebaysdk.merchandising import Connection as Merchandising
    return Merchandising(*args, **kwargs)

def html(*args, **kwargs):
    from ebaysdk.http import Connection as HTTP
    return HTTP(*args, **kwargs)

def parallel(*args, **kwargs):
    from ebaysdk.parallel import Parallel
    return Parallel(*args, **kwargs)

