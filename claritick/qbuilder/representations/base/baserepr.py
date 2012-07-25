import datetime
import time

class BaseRepresentation(object):
    def __init__(self, qbuilder, logger, title = None):
        self.qbuilder = qbuilder
        self.logger = logger
        self.title = self.qbuilder.query_parameters.get('title','Query Builder')

    def makefloatfromstuff(self, stuff):
        if isinstance(stuff, (int, float)):
            return float(stuff)
        if isinstance(stuff, basestring) or stuff is None:
            return 0.
        if isinstance(stuff, datetime.timedelta):
            return stuff.days * 24*60*60 + stuff.seconds
        if isinstance(stuff, datetime.datetime):
            return time.mktime(stuff.timetuple())

    def represent(self):
        self.logger.error(u"Should not call 'represent' on this base class.")
        return u"Not implemented, please define me"
