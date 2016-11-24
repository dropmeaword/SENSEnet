
__author__ = "Luis Rodil-Fernandez <root@derfunke.net>"
__version__ = "0.2b"

def find_arduinos():
    return glob.glob('/dev/cu.wchusb*') + glob.glob('/dev/tty.usbserial-*')
