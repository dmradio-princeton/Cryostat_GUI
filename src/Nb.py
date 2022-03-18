import serial
from sensopy import sys, os

from collections import namedtuple

Pair = namedtuple("Pair", ["t", "v"])

pairs = [Pair(400.0, 0.27456), Pair(300.0, 0.51892), Pair(24.0, 1.13698), Pair(10.0, 1.42014), Pair(1.4,1.69812), Pair(1.0,1.80)]

class Nb:
    """
    Class for serial communication with NB's through
    erlang port.
    """
    baud = 115200
    term = b'\xfe'
    timeout = 0.5
    queries = {
        'D1': 'D1V\r',
        'D2': 'D2V\r',
        'D3': 'D3V\r',
        'D4': 'D4V\r',
        'D5': 'D5V\r',
        'R1': 'R1Q\r',
        'R2': 'R2Q\r',
        'R3': 'R3Q\r',
    }

    def __init__(self, port, sensors):
        """
        Initialize with device port
        and list of messages to send
        in order to query all live sensors.
        """
        self.port = port
        self.serial = serial.Serial(
            port,
            Nb.baud,
            serial.EIGHTBITS,
            serial.PARITY_ODD,
            serial.STOPBITS_ONE,
            timeout=Nb.timeout,
        )
        if sensors is None:
            self.queries = Nb.queries
        else:
            queries = {}
            for sensor in sensors:
                queries[sensor] = Nb.queries[sensor]
            self.queries = queries

    def std_write(self, cmd_char, sensor, val):
        """Write a standard command message
        """
        msg = '%s%s %s\r' % (sensor, cmd_char, val,)
        self.serial.write(msg.encode())

    def query(self, msg):
        """
        Write msg, then read from serial port.
        Nb.timeout is timeout on reading the return msg.
        """
        ## use flushInput and flushOutput
        ## instead of flush, to discard data
        self.serial.flushInput()
        self.serial.flushOutput()
        self.serial.write(msg.encode())

        c = ''
        s = ''
        try:
            while c != Nb.term:
                c = self.serial.read(1)
                if c != b'\xa1' and c !=b'\xc8' and c != b'\xfe': 
                    s += c.decode()
        except KeyboardInterrupt:
            return s
        else:
            return s


    def handle_Q(self):
        """Query for all data.
        """
        self.is_connected = True
        d = {}
        for sensor in self.queries:
                d[sensor] = self.query(Nb.queries[sensor])
        return d

    def handle_H(self, sensor, state):
        """Set heater State (on/off).
        """
        return self.std_write('H', sensor, state)

    def handle_S(self, sensor, sp):
        """Set setpoint.
        """
        return self.std_write('S', sensor, sp)

    def handle_P(self, sensor, p):
        """Set P in PI loop.
        """
        return self.std_write('P', sensor, p)

    def handle_I(self, sensor, i):
        """Set I in PI loop.
        """
        return self.std_write('I', sensor, i)

    def handle_E(self, sensor, i):
        """Set E for RuOx.
        """
        return self.std_write('E', sensor, i)

    def handle_halt(self):
        raise Exception("halt request received")
