__author__ = 'Robin Quetin'
from cherrypy import HTTPRedirect
from urllib2 import quote


class CairisHTTPError(object):
    def __init__(self, msg, code=400, status='Bad Request'):
        msg = quote(msg)
        status = quote(status)
        raise HTTPRedirect('/exception?code={0}&title={1}&msg={2}'.format(code, status, msg))