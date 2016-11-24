import logging
import serial
import time
from nodes import *
from nodes.controller import *
import OSC
from OSC import *
from pylsl import StreamInfo, StreamOutlet, local_clock

class BalanceBoardSerialIn(Inlet):
    SEPARATOR = " "
    def __init__(self, root, device, bitrate):
        ch = "Serial({0}, {1})".format(device, bitrate)
        super(BalanceBoardSerialIn, self).__init__(root, ch)
        try:
            logging.debug("Opening serial device @ {0} at bitrate {1}".format(device, bitrate) )
            self.serial = serial.Serial(device, bitrate)
            time.sleep(.2)
            self.serial.flush()
        except OSError as e:
            logging.error("(!!!) Failed to open serial pipe @ ", device)
            raise e

    def work(self):
        line = None
        try:
            line = self.serial.readline()

            values = line.strip().split(BalanceBoardSerialIn.SEPARATOR)

            #print values

            # parse incoming line into the balanceboard protocol
            retval = {}
            retval['sensor_id'] = values[0]
            retval['seq'] = int(values[1])
            retval['millis'] = int(values[2])
            retval['micro'] = int(values[3])
            retval['accx'] = float(values[4])
            retval['accy'] = float(values[5])
            retval['accz'] = float(values[6])
            # retval['gyrox'] = float(values[7])
            # retval['gyroy'] = float(values[8])
            # retval['gyroz'] = float(values[9])
            retval['laccx'] = float(values[7])
            retval['laccy'] = float(values[8])
            retval['laccz'] = float(values[9])
            retval['yaw'] = float(values[10])
            retval['pitch'] = float(values[11])
            retval['roll'] = float(values[12])

            return self.pump(retval)
        except serial.serialutil.SerialException, e:
            logging.fatal("couldn't read from serial")
            raise e
        except Exception, e:
            logging.debug("failed parsing incoming line: '{0}'".format(line))
            return None

    def shutdown(self):
        if self.serial:
            self.serial.close()

class BalanceBoardOscOut(Outlet):
    def __init__(self, root, host, port):
        super(BalanceBoardOscOut, self).__init__(root, "OscOut({0}:{1})".format(host, port))
        logging.debug("Opening OSC connection to {0}:{1}".format(host, port) )
        self.osctx = OSCClient()
        self.dest = (host, port)
        self.osctx.connect( self.dest )

    def work(self, data):
        msg = OSCMessage()
        msg.setAddress("/node/bboard/{0}".format(self.root.id))
        msg.append(data['seq'])
        msg.append(data['accx'])
        msg.append(data['accy'])
        msg.append(data['accz'])
        # msg.append(data['gyrox'])
        # msg.append(data['gyroy'])
        # msg.append(data['gyroz'])
        msg.append(data['laccx'])
        msg.append(data['laccy'])
        msg.append(data['laccz'])
        msg.append(data['yaw'])
        msg.append(data['pitch'])
        msg.append(data['roll'])
        #logging.debug( str(msg) )
        try:
            self.osctx.send( msg )
            self.pump(msg)
        except OSC.OSCClientError as e:
            logging.info("OSC connection with peer was lost, retrying.")
            self.osctx.connect( self.dest )

    def shutdown(self):
        pass


class BalanceBoardLSLOut(Outlet):
    def __init__(self, root, datarate=250):
        super(BalanceBoardLSLOut, self).__init__(root, "LSLOut")
        logging.debug("Configuring LSL stream for 'wobble' data...")
        # configure LSL stream
        self.info = StreamInfo('BalanceBoard', 'wobble', 9, datarate, 'float32', self.root.id)
        # append some meta-data
        self.info.desc().append_child_value("manufacturer", "play")
        channels = self.info.desc().append_child("channels")
        for c in ["accx", "accy", "accz", "acclinx", "accliny", "acclinz", "yaw", "pitch", "roll"]:
            channels.append_child("channel") \
                .append_child_value("label", c) \
                .append_child_value("type", "wobble")

        # next make an outlet; we set the transmission chunk size to 32 samples and
        # the outgoing buffer size to 360 seconds (max.)
        self.outlet = StreamOutlet(self.info, 32, 360)

    def work(self, data):
        sample = [data['accx'], data['accy'], data['accz'],
            data['laccx'], data['laccy'], data['laccz'],
            data['yaw'], data['pitch'], data['roll']]
            # ,
            # data['yaw'], data['pitch'], data['roll']]
        # get a time stamp in seconds
        stamp = local_clock()
        # now send it
        self.outlet.push_sample(sample, stamp)
        self.pump(sample)

    def shutdown(self):
        pass


class BalanceBoard(AbstractController):
    def __init__(self, sid):
        super(BalanceBoard, self).__init__(sid)
        pass
