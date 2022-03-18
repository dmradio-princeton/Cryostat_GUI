from PyQt5 import QtWidgets, QtCore
from Data import Data

from Plot import Plot

import datetime, time

class SignalGenerator:
    def __init__(self, dev):
        self.data = dev['data']

        self._widgets()
        self._connections()
        self._layout()

    def _widgets(self):
        self.freq_label= QtWidgets.QLabel("Frequency (Hz):")
        self.ampl_label= QtWidgets.QLabel("Amplitude (V):")
        self.offset_label= QtWidgets.QLabel("Offset (V):")

        self.function = QtWidgets.QComboBox()
        self.function.addItem("SIN")
        self.function.addItem("SQU")
        self.function.addItem("RAMP")
        self.function.addItem("PULS")
        self.function.addItem("NOIS")

        self.freq = QtWidgets.QLineEdit("")
        self.ampl = QtWidgets.QLineEdit("")
        self.offset = QtWidgets.QLineEdit("")

        self.apply_button = QtWidgets.QPushButton('Apply')
        self.stop_button = QtWidgets.QPushButton('Stop')

        self.spac_label= QtWidgets.QLabel("Spacing for the Sweep.:")
        self.start_freq_label= QtWidgets.QLabel("Start Frequency (Hz):")
        self.stop_freq_label= QtWidgets.QLabel("Stop Frequency (Hz):")
        self.time_label= QtWidgets.QLabel("Time (s):")

        self.spac = QtWidgets.QComboBox()
        self.spac.addItem("LIN")
        self.spac.addItem("LOG")

        self.start_freq = QtWidgets.QLineEdit("")
        self.stop_freq = QtWidgets.QLineEdit("")
        self.time = QtWidgets.QLineEdit("")

        self.sweep_on_button = QtWidgets.QPushButton('Sweep ON')
        self.sweep_off_button = QtWidgets.QPushButton('Sweep OFF')


    def _layout(self):
        self.groupBox_apply = QtWidgets.QGroupBox("Apply")
        self.groupBox_sweep = QtWidgets.QGroupBox("Sweep")

        self.grid_apply = QtWidgets.QGridLayout()
        self.grid_sweep = QtWidgets.QGridLayout()

        self.grid = QtWidgets.QGridLayout()

        self.grid_apply.addWidget(self.freq_label, 1, 0)
        self.grid_apply.addWidget(self.ampl_label, 2, 0)
        self.grid_apply.addWidget(self.offset_label, 3, 0)

        self.grid_apply.addWidget(self.function, 0, 1)
        self.grid_apply.addWidget(self.freq, 1, 1)
        self.grid_apply.addWidget(self.ampl, 2, 1)
        self.grid_apply.addWidget(self.offset, 3, 1)

        self.grid_sweep.addWidget(self.spac_label, 0, 0)
        self.grid_sweep.addWidget(self.start_freq_label, 1, 0)
        self.grid_sweep.addWidget(self.stop_freq_label, 2, 0)
        self.grid_sweep.addWidget(self.time_label, 3, 0)

        self.grid_sweep.addWidget(self.spac, 0, 1)
        self.grid_sweep.addWidget(self.start_freq, 1, 1)
        self.grid_sweep.addWidget(self.stop_freq, 2, 1)
        self.grid_sweep.addWidget(self.time, 3, 1)

        self.grid_sweep.addWidget(self.sweep_on_button, 4, 0, 1, 2)
        self.grid_sweep.addWidget(self.sweep_off_button, 5, 0, 1, 2)


        self.groupBox_apply.setLayout(self.grid_apply)
        self.groupBox_sweep.setLayout(self.grid_sweep)

        self.grid.addWidget(self.groupBox_apply, 0, 0)
        self.grid.addWidget(self.groupBox_sweep, 0, 1)

        self.grid.addWidget(self.apply_button, 1, 0, 1, 2)
        self.grid.addWidget(self.stop_button, 2, 0, 1, 2)

    def _connections(self):
        self.apply_button.clicked.connect(self.apply)
        self.stop_button.clicked.connect(self.stop)

        self.sweep_on_button.clicked.connect(self.sweep_on)
        self.sweep_off_button.clicked.connect(self.sweep_off)

    def apply(self):
        function = self.function.currentText()

        global freq
        freq = self.freq.text()

        ampl = self.ampl.text()
        offset = self.offset.text()

        self.command = "APPL:{} {} HZ, {} VPP, {} V".format(function,freq,ampl,offset)
        self.data.write(self.command)

    def stop(self):
        self.data.write("OUTP OFF")

    def sweep_on(self):
        start_freq = "FREQ:STAR {} HZ".format(self.start_freq.text())
        stop_freq = "FREQ:STOP {} HZ".format(self.stop_freq.text())
        spac = "SWE:SPAC LIN".format(self.spac.currentText())
        time = "SWE:TIME {}".format(self.time.text())

        self.data.write(start_freq)
        self.data.write(stop_freq)
        self.data.write(spac)
        self.data.write(time)

        self.data.write("SWE:STAT ON")

    def sweep_off(self):
        self.data.write("SWE:STAT OFF")
