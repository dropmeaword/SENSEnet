from nodes import *
from time import time

class LowPass(Inlet):
    """
        Implement a simple Low-Pass filter using the discrete-time
        implementation:

        y = k * x + (1 - k) * y0

        where x is the current reading, y0 is the previous reading and k
        is a smoothing factor where 0 <= k <= 1.

        see: https://theccontinuum.com/2012/09/24/arduino-imu-pitch-roll-from-accelerometer/
    """
    def __init__(self, root, forwardto, k=.025):
        super(LowPass, self).__init__(root, "LowPass({0})".format(k))
        logging.debug("Setting low-pass on inlet with smoothing factor = {0}".format(k) )
        self.k = k
        self.forwardto = forwardto
        self.lastreading = []

    def work(self, data):
        # make sure lastdata always contains at least one complete sample
        if len(self.lastreading) == 0:
            self.lastreading = data

        idx = 0
        for r in data:  #
            self.lastreading[idx] = data[idx] * self.k + (self.lastreading[idx] * (1.0 - self.k))

        # forward to node
        self.forwardto.work(self.lastreading)

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
