from nodes import *
from time import time

class RateLimiter(Outlet):
    """
        Implement a simple rate limitter that forward messages to another object.
    """
    def __init__(self, root, forwardto, rate=50):
        super(RateLimiter, self).__init__(root, "RateLimiter({0})".format(rate))
        logging.debug("Setting a rate limitter for outlet at rate {0}".format(rate) )
        self.forward = forwardto
        self.rate = rate
        self.lastpacket = 0
        self.mustelapse = 1.0 / rate

    def work(self, data):
        elapsed = time() - self.lastpacket
        if elapsed > self.mustelapse:
            # forward a data packet only if the
            self.forward.work(data)
            self.lastpacket = time()
