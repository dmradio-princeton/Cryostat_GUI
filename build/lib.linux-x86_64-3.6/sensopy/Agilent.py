import os


class usbDevice(object):
    """Initializes a connection to the device port (presumably USB)"""

    def __init__(self, location):
        self.device = location
        self.connect = os.open(location, os.O_RDWR)

    def write(self, command):
        os.write(self.connect, command)

    def read(self, length=4000):
        return os.read(self.connect, length)

    def getID(self):
        self.write(str.encode("*IDN?"))
        return self.read(100)


class instrument(object):
    """Initialize instrument given a port, e.g. /dev/usbtmc0/"""

    def __init__(self, location):
        self.port = usbDevice(location)
        self.id = self.port.getID()
        print(self.id.decode("utf-8"))

    def write(self, command):
        self.port.write(str.encode(command))

    def read(self, command):
        return self.port.read(command).decode("utf-8")


#if __name__ == '__main__':
#    agilent = instrument("/dev/usbtmc0")
#    agilent.write("OUTP OFF")
#    agilent.write(f"APPL:SIN 0.1 HZ, 15.0 VPP, 0 V")
   # agilent.write(f"FREQ:STAR 5 KHZ")
   # agilent.write(f"FREQ:STOP 15 KHZ")
   # agilent.write(f"SWE:SPAC LIN")
   # agilent.write(f"SWE:TIME 10")
   # agilent.write("SWE:STAT ON")
