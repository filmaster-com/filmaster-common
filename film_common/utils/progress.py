import time, datetime
import inspect
import logging
logger = logging.getLogger(__name__)

class Progress(object):
    def __init__(self, total, message="", level=logging.INFO, format="%(message)s %(percentage)s ETA: %(ETA)s"):
        f = inspect.currentframe()
        self.logger = f and f.f_back and f.f_back.f_globals.get('logger') or logger
        self.message = message
        self.level = level
        self.cnt = 0
        self.total = total
        self.last_perc = None
        self.start_time = time.time()
        self.format = format

    def tick(self, n=1):
        self.cnt += n
        p = min(self.cnt * 100.0 / self.total, 100.0)
        perc = "%5.1f%%" % p
        if perc != self.last_perc:
            now = time.time()
            t = now - self.start_time
            total_t = t * self.total / self.cnt
            eta = datetime.datetime.now() + datetime.timedelta(seconds=total_t-t)
            message = self.format % {
                    'message': self.message,
                    'percentage': perc,
                    'ETA': eta,
                    'cnt': self.cnt,
                    'total': self.total,
            }
            self.logger.log(self.level, message)
            self.last_perc = perc

