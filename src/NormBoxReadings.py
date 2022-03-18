from PyQt5 import QtWidgets, QtCore
from Data import Data

import datetime, time

class NormBoxReadings:
    def __init__(self, dev):

        self.dev = dev
        self.data = dev['data']
        self.folder = dev['folder']
        self.ports = dev['ports']
        self.sensors = dev['sensors']

        self.pids = ["SP", "P", "I", "E"]

        self._widgets()
        self._connections()
        self._layout()
        self._settings()

    def _widgets(self):
        self.con_com = {}
        self.status = {}
        self.meas = {}
        self.meas_label = {}

        self.H = {}
        self.H_label = {}
        self.H_sensors = {}
        self.H_button = {}

        self.item = {}
        self.item_label = {}
        self.item_sensors = {}
        self.item_button = {}

        for port in self.ports:
            self.con_com[port] = QtWidgets.QPushButton('Connect/Refresh')
            self.meas[port] = {}
            self.meas_label[port] = {}
            for sensor in self.sensors:
                self.meas[port][sensor] = QtWidgets.QLineEdit("")
                self.meas_label[port][sensor] = QtWidgets.QLabel("{}:".format(sensor))

            self.H[port] = QtWidgets.QDoubleSpinBox()
            self.H[port].setRange(0, 150)
            self.H_label[port] = QtWidgets.QLabel("H:")
            self.H_sensors[port] = QtWidgets.QComboBox()
            self.H_sensors[port].addItems(["D1", "D2", "D3", "R1", "R2", "R3"])
            self.H_button[port] = QtWidgets.QPushButton('Set')

            self.item[port] = {}
            self.item_label[port] = {}
            self.item_sensors[port] = {}
            self.item_button[port] = {}
            for pid in self.pids:
                self.item[port][pid] = QtWidgets.QDoubleSpinBox()
                self.item_label[port][pid] = QtWidgets.QLabel(pid +":")
                self.item_sensors[port][pid] = QtWidgets.QComboBox()
                if pid == "E":
                    self.item_sensors[port][pid].addItems(["R1", "R2", "R3"])
                else:
                    self.item_sensors[port][pid].addItems(["D1", "D2", "D3", "R1", "R2", "R3"])
                if pid == "SP":
                    self.item[port][pid].setRange(1, 5000)
                elif pid == "I" or pid == "E":
                    self.item[port][pid].setRange(0, 100)
                else:
                    self.item[port][pid].setRange(1, 100)
                self.item_button[port][pid] = QtWidgets.QPushButton('Set')


    def _layout(self):
        self.grid = QtWidgets.QGridLayout()

        hbox = {}
        gbox_meas = {}
        gbox = {}

        groupBox_con = {}
        groupBox_meas = {}
        groupBox_set = {}

        groupBox_port = {}
        vbox_port = {}

        p = 0
        for port in self.ports:
            gbox_meas[port] = QtWidgets.QGridLayout()
            gbox[port] = QtWidgets.QGridLayout()
            vbox_port[port] = QtWidgets.QVBoxLayout()

            k = 0
            for sensor in self.sensors:
                gbox_meas[port].addWidget(self.meas_label[port][sensor], k, 0)
                gbox_meas[port].addWidget(self.meas[port][sensor], k, 1)
                k += 1

            r = 0
            for pid in self.pids:
                gbox[port].addWidget(self.item_label[port][pid], r, 2)
                gbox[port].addWidget(self.item_sensors[port][pid], r, 3)
                gbox[port].addWidget(self.item[port][pid], r, 4)
                gbox[port].addWidget(self.item_button[port][pid], r, 5)

                r += 1

            gbox[port].addWidget(self.H_label[port], r, 2)
            gbox[port].addWidget(self.H_sensors[port], r, 3)
            gbox[port].addWidget(self.H[port], r, 4)
            gbox[port].addWidget(self.H_button[port], r, 5)

            groupBox_meas[port] = QtWidgets.QGroupBox("Readings")
            groupBox_meas[port].setLayout(gbox_meas[port])

            groupBox_set[port] = QtWidgets.QGroupBox("Settings")
            groupBox_set[port].setLayout(gbox[port])

            vbox_port[port].addWidget(self.con_com[port])
            vbox_port[port].addWidget(groupBox_meas[port])
            vbox_port[port].addWidget(groupBox_set[port])

            groupBox_port[port] = QtWidgets.QGroupBox("Norm's Box " + str(p + 1))
            groupBox_port[port].setLayout(vbox_port[port])

            self.grid.addWidget(groupBox_port[port], 0, p)
            p += 1

    def _connections(self):
        for port in self.ports:
            self.con_com[port].clicked.connect(lambda checked, arg=port: self.con_com_handler(arg))

    def _settings(self):
        for port in self.ports:
            for pid in self.pids:
                if pid == "SP":
                    self.item_button[port][pid].clicked.connect(lambda checked, arg1 = port, arg2 = pid:
self.SP_handler(arg1, self.item_sensors[arg1][arg2].currentText(), self.item[arg1][arg2].value()))
                elif pid == "P":
                    self.item_button[port][pid].clicked.connect(lambda checked, arg1 = port, arg2 = pid:
self.P_handler(arg1, self.item_sensors[arg1][arg2].currentText(), self.item[arg1][arg2].value()))
                elif pid == "I":
                    self.item_button[port][pid].clicked.connect(lambda checked, arg1 = port, arg2 = pid:
self.I_handler(arg1, self.item_sensors[arg1][arg2].currentText(), self.item[arg1][arg2].value()))
                elif pid == "E":
                    self.item_button[port][pid].clicked.connect(lambda checked, arg1 = port, arg2 = pid:
self.E_handler(arg1, self.item_sensors[arg1][arg2].currentText(), self.item[arg1][arg2].value()))

            self.H_button[port].clicked.connect(lambda checked, arg = port: self.H_handler(arg, self.H_sensors[arg].currentText(), self.H[arg].value()))

    def con_com_handler(self, port):
        self.Data = Data(self.dev, port)
        for sensor in self.sensors:
            self.Data.get_reading(sensor)
            self.meas[port][sensor].setText(str(self.Data.line))

    def SP_handler(self, port, sensor, sp):
        self.data[port].handle_S(sensor, sp)

    def P_handler(self, port, sensor, p):
        self.data[port].handle_P(sensor, p)

    def I_handler(self, port, sensor, i):
        self.data[port].handle_I(sensor, i)

    def E_handler(self, port, sensor, e):
        self.data[port].handle_E(sensor, e)

    def H_handler(self, port, sensor, h):
        self.data[port].handle_H(sensor, h)
