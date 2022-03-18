from PyQt5 import QtWidgets, QtCore
from Data import Data

import datetime, time

class SensorayReadings:
    def __init__(self, dev):

        self.dev = dev
        self.data = dev['data']
        self.folder = dev['folder']
        self.iomports = dev['ports']
        self.in_chans = dev['sensors']
        self.out_chans = dev['out_chans']

        self.N_channels = self.in_chans[-1] + 1

        self._widgets()
        self._layout()
        self._connections()

    def _widgets(self):
        self.iomport_label = {}
        self.ain_label = {}
        self.aout_label = {}

        self.ain = {}
        self.aout = {}

        self.set_aout = {}
        self.set_aout_button = {}

        self.ain_connect_button = {}
        self.aout_connect_button = {}
        for iomport in self.iomports:
            self.ain_label[iomport] = {}
            self.aout_label[iomport] = {}

            self.ain[iomport] = {}
            self.aout[iomport] = {}

            self.set_aout[iomport] = {}
            self.set_aout_button[iomport] = {}

            self.ain_connect_button[iomport] = QtWidgets.QPushButton('Connect/Refresh')
            self.aout_connect_button[iomport] = QtWidgets.QPushButton('Connect/Refresh')
            for chan in self.in_chans:
                self.ain_label[iomport][chan] = QtWidgets.QLabel("Channel " + str(chan) + ":")
                self.ain[iomport][chan] = QtWidgets.QLineEdit("")

                if chan <= 7:
                    self.aout_label[iomport][chan] = QtWidgets.QLabel("Channel " + str(chan) + ":")
                    self.aout[iomport][chan] = QtWidgets.QLineEdit("")
                    self.set_aout[iomport][chan] = QtWidgets.QDoubleSpinBox()
                    self.set_aout[iomport][chan].setRange(0, 10)
                    self.set_aout_button[iomport][chan] = QtWidgets.QPushButton('Set')

        self.cycle_on_button = {}
        self.cycle_off_button = {}
        for cycle in range(3):
            self.cycle_on_button[cycle] = QtWidgets.QPushButton('On')
            self.cycle_off_button[cycle] = QtWidgets.QPushButton('Off')

    def _layout(self):
        self.grid = QtWidgets.QGridLayout()

        group_grid_ain = {}
        group_grid_aout = {}
        group_grid_iom = {}

        group_Box_ain = {}
        group_Box_aout = {}
        group_Box_iom = {}

        i = 0
        for iomport in self.iomports:
            group_grid_ain[iomport] = QtWidgets.QGridLayout()
            group_grid_aout[iomport] = QtWidgets.QGridLayout()
            group_grid_iom[iomport] = QtWidgets.QGridLayout()

            group_Box_ain[iomport] = QtWidgets.QGroupBox(" AINs:")
            group_Box_aout[iomport] = QtWidgets.QGroupBox(" AOUTs:")
            group_Box_iom[iomport] = QtWidgets.QGroupBox("IOM port " + str(iomport) + " :")

            group_grid_ain[iomport].addWidget(self.ain_connect_button[iomport], 0, 0)
            group_grid_aout[iomport].addWidget(self.aout_connect_button[iomport], 0, 0)

            group_grid_aout[iomport].addWidget(QtWidgets.QLabel("Readings:"), 1, 1)
            group_grid_aout[iomport].addWidget(QtWidgets.QLabel("Settings (V):"), 1, 2)

            for chan in self.in_chans:
                if chan < self.N_channels/2:
                    group_grid_ain[iomport].addWidget(self.ain_label[iomport][chan], chan + 1, 0)
                    group_grid_ain[iomport].addWidget(self.ain[iomport][chan], chan + 1, 1)

                    group_grid_aout[iomport].addWidget(self.aout_label[iomport][chan], chan + 2, 0)
                    group_grid_aout[iomport].addWidget(self.aout[iomport][chan], chan + 2, 1)

                    group_grid_aout[iomport].addWidget(self.set_aout[iomport][chan], chan + 2, 2)
                    group_grid_aout[iomport].addWidget(self.set_aout_button[iomport][chan], chan + 2, 3)
                else:
                    group_grid_ain[iomport].addWidget(self.ain_label[iomport][chan], (chan-self.N_channels/2) + 1, 0 + 2)
                    group_grid_ain[iomport].addWidget(self.ain[iomport][chan], (chan-self.N_channels/2) + 1, 1 + 2)

            group_Box_ain[iomport].setLayout(group_grid_ain[iomport])
            group_Box_aout[iomport].setLayout(group_grid_aout[iomport])

            group_grid_iom[iomport].addWidget(group_Box_ain[iomport], 0, 0)
            group_grid_iom[iomport].addWidget(group_Box_aout[iomport], 1, 0)

            group_Box_iom[iomport].setLayout(group_grid_iom[iomport])

            self.grid.addWidget(group_Box_iom[iomport], 0, i)

            i += 1

        group_cycle = {}
        hbox_cycle = {}
        for cycle in range(3):
            if cycle == 0:
                group_cycle[cycle] = QtWidgets.QGroupBox("3He gas-gap heat-switch")
            else:
                group_cycle[cycle] = QtWidgets.QGroupBox("4He{} gas-gap heat-switch".format(cycle))

            hbox_cycle[cycle] = QtWidgets.QHBoxLayout()

            hbox_cycle[cycle].addWidget(self.cycle_on_button[cycle])
            hbox_cycle[cycle].addWidget(self.cycle_off_button[cycle])

            group_cycle[cycle].setLayout(hbox_cycle[cycle])

            self.grid.addWidget(group_cycle[cycle], 1 + cycle, 0 , 1, 2)

    def _connections(self):
        volts = {}
        for iomport in self.iomports:
            volts[iomport] = {}
            self.ain_connect_button[iomport].clicked.connect(lambda checked, arg=iomport: self.ain_readings(arg))
            self.aout_connect_button[iomport].clicked.connect(lambda checked, arg=iomport: self.aout_readings(arg))

            for chan in self.out_chans:
               self.set_aout_button[iomport][chan].clicked.connect(lambda checked, arg1=iomport, arg2=chan:
self.aout_settings(arg1, arg2, self.set_aout[arg1][arg2].value()))

        for cycle in range(3):
            self.cycle_on_button[cycle].clicked.connect(lambda checked, arg=cycle: self.turn_on_heat_switch(arg))
            self.cycle_off_button[cycle].clicked.connect(lambda checked, arg=cycle: self.turn_off_heat_switch(arg))

    def ain_readings(self, iomport):
        self.Data = Data(self.dev,iomport)
        for chan in self.in_chans:
            self.Data.get_reading(chan)
            self.ain[iomport][chan].setText(self.Data.line)
    
    def aout_readings(self, iomport):
        for chan in self.out_chans:
            self.aout[iomport][chan].setText(str(self.data[iomport].get_aout(chan)))

    def aout_settings(self, iomport, chan, volts):
        self.data[iomport].set_aout(chan, volts)

    def turn_on_heat_switch(self, cycle):
        if cycle == 0:
            self.data[15].set_aout(1, 10)
            time.sleep(1)
            self.data[15].set_aout(1, 0)
        elif cycle == 1:
            self.data[15].set_aout(3, 10)
            time.sleep(1)
            self.data[15].set_aout(3, 0)
        elif cycle == 2:
            self.data[15].set_aout(5, 10)
            time.sleep(1)
            self.data[15].set_aout(5, 0)

    def turn_off_heat_switch(self, cycle):
        if cycle == 0:
            self.data[15].set_aout(0, 10)
            time.sleep(1)
            self.data[15].set_aout(0, 0)
        elif cycle == 1:
            self.data[15].set_aout(2, 10)
            time.sleep(1)
            self.data[15].set_aout(2, 0)
        elif cycle == 2:
            self.data[15].set_aout(4, 10)
            time.sleep(1)
            self.data[15].set_aout(4, 0)
