# -*- coding: utf-8 -*-

'''
© 2012-2013 eBay Software Foundation
Authored by: Tim Keefer
Licensed under CDDL 1.0
'''

class ConnectionError(Exception):
    def __init__(self, msg, response):
        super(ConnectionError, self).__init__(u'%s' % msg)
        self.message = u'%s' % msg
        self.response = response

    def __str__(self):
        return repr(self.message)

class ConnectionConfigError(Exception):
    def __init__(self, msg):
        super(ConnectionConfigError, self).__init__(u'%s' % msg)
        self.message = u'%s' % msg

    def __str__(self):
        return repr(self.message)

class ConnectionResponseError(Exception):
    def __init__(self, msg, response):
        super(ConnectionResponseError, self).__init__(u'%s' % msg)
        self.message = u'%s' % msg
        self.response = response

    def __str__(self):
        return repr(self.message)

class RequestPaginationError(Exception):
    def __init__(self, msg, response):
        super(RequestPaginationError, self).__init__(u'%s' % msg)
        self.message = u'%s' % msg
        self.response = response

    def __str__(self):
        return repr(self.message)

class PaginationLimit(Exception):
    def __init__(self, msg, response):
        super(PaginationLimit, self).__init__(u'%s' % msg)
        self.message = u'%s' % msg
        self.response = response

    def __str__(self):
        return repr(self.message)
