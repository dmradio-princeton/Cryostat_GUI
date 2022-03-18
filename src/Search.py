from PyQt5 import QtWidgets, QtCore
from Data import Data
from pathlib import Path

import datetime, time, sys, os, re

class Search:
    def __init__(self, dev_nb, dev_sens):
   # def __init__(self, dev_nb):

        self.dev_nb = dev_nb 
        self.ports  = dev_nb['ports']
        self.sensors  = dev_nb ['sensors']

        self.dev_sens = dev_sens
        #self.iomports = dev_sens['ports']
        self.iomports = [7]
        self.in_chans = dev_sens['sensors']
        self.out_chans = dev_sens['out_chans']

        self.N_channels = self.in_chans[-1] + 1

        self._widgets()
        self._layout()

        self.timer = QtCore.QTimer()

    def _widgets(self):
        self.con_com = {}
        self.status = {}
        self.meas = {}
        self.meas_label = {}

        for port in self.ports:
            self.meas[port] = {}
            self.meas_label[port] = {}
            for sensor in self.sensors:
                self.meas_label[port][sensor] = QtWidgets.QLabel("{}: ".format(sensor))
                self.meas[port][sensor] = QtWidgets.QLineEdit("")

        self.search_line = QtWidgets.QLineEdit("Enter date and time as: 'mm-dd-yy_HH:MM:SS'")
        self.search_button = QtWidgets.QPushButton('Search')
        self.search_button.clicked.connect(self.search)

        self.log_button = QtWidgets.QPushButton('Start log')
        self.log_button.clicked.connect(self.log)

        self.stop_log_button = QtWidgets.QPushButton('Stop log')
        self.stop_log_button.clicked.connect(self.stop_log)

        self.iomport_label = {}
        self.ain_label = {}

        self.ain = {}

        for iomport in self.iomports:
            self.ain_label[iomport] = {}

            self.ain[iomport] = {}

            for chan in self.in_chans:
                self.ain_label[iomport][chan] = QtWidgets.QLabel("Channel " + str(chan) + ":")
                self.ain[iomport][chan] = QtWidgets.QLineEdit("")


    def _layout(self):
        self.grid = QtWidgets.QGridLayout()

        gbox_meas = {}
        gbox = {}

        groupBox_con = {}
        groupBox_meas = {}
        groupBox_set = {}

        groupBox_port = {}
        vbox_port = {}

        self.group_Box_search = QtWidgets.QGroupBox("Search:")

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

            groupBox_meas[port] = QtWidgets.QGroupBox("Readings")
            groupBox_meas[port].setLayout(gbox_meas[port])

            vbox_port[port].addWidget(groupBox_meas[port])

            groupBox_port[port] = QtWidgets.QGroupBox("Norm's Box " + str(p + 1))
            groupBox_port[port].setLayout(vbox_port[port])

            self.grid.addWidget(groupBox_port[port], 0 , 2*p , 1 , 2)
            p += 1

        group_grid_ain = {}
        group_grid_iom = {}

        group_Box_ain = {}
        group_Box_iom = {}

        self.group_Box_search = QtWidgets.QGroupBox("Search:")

        i = 0
        for iomport in self.iomports:
            group_grid_ain[iomport] = QtWidgets.QGridLayout()
            group_grid_iom[iomport] = QtWidgets.QGridLayout()

            group_Box_ain[iomport] = QtWidgets.QGroupBox(" AINs:")
            group_Box_iom[iomport] = QtWidgets.QGroupBox("IOM port " + str(iomport) + " :")


            for chan in self.in_chans:
                if chan < self.N_channels/2:
                    group_grid_ain[iomport].addWidget(self.ain_label[iomport][chan], chan + 1, 0)
                    group_grid_ain[iomport].addWidget(self.ain[iomport][chan], chan + 1, 1)

                else:
                    group_grid_ain[iomport].addWidget(self.ain_label[iomport][chan], (chan-self.N_channels/2) + 1, 0 + 2)
                    group_grid_ain[iomport].addWidget(self.ain[iomport][chan], (chan-self.N_channels/2) + 1, 1 + 2)

            group_Box_ain[iomport].setLayout(group_grid_ain[iomport])

            group_grid_iom[iomport].addWidget(group_Box_ain[iomport], 0, 0)

            group_Box_iom[iomport].setLayout(group_grid_iom[iomport])

            self.grid.addWidget(group_Box_iom[iomport], 1, 3*i , 1 , 3)

            i += 1

        self.grid.addWidget(self.search_line, 2 , 0 , 1 , 3)
        self.grid.addWidget(self.search_button, 2 , 3 , 1 , 3)
        self.grid.addWidget(self.log_button, 3 , 0 , 1 , 6)
        self.grid.addWidget(self.stop_log_button, 4 , 0 , 1 , 6)

    def search(self):
        self.t_search = float(time.mktime(datetime.datetime.strptime(self.search_line.text(), '%m-%d-%y_%H:%M:%S').timetuple()))

        self.folder = self.dev_nb['folder']
        for port in self.ports:
            for sensor in self.sensors:
                self.meas[port][sensor].setText(self.process_search(port, sensor))

        self.folder = self.dev_sens['folder']
        for iomport in self.iomports:
            for chan in self.in_chans:
                self.ain[iomport][chan].setText(self.process_search(iomport, chan))

    def process_search(self, port, sensor):
        self.curve = "{}".format(sensor)
        self.current_port = re.search(r'\d+', str(port)).group()

        self.dir_path = os.path.join(self.folder, self.current_port)
        self.file_path_full = os.path.join(self.dir_path, self.curve + ".txt")

        if os.path.exists(self.file_path_full):
            self.temp = None
            with open(self.file_path_full) as f:
                for line in f:
                    if (self.t_search  < float(line.split(" ", 1)[0])):
                        return self.temp
                        break
                    self.temp = line.split(" ", 1)[1]

    def last_value_search(self, port, sensor):
        self.curve = "{}".format(sensor)
        self.current_port = re.search(r'\d+', str(port)).group()

        self.dir_path = os.path.join(self.folder, self.current_port)
        self.file_path_full = os.path.join(self.dir_path, self.curve + ".txt")

        if os.path.exists(self.file_path_full):
            with open(self.file_path_full) as f:
                last_line = f.readlines()[-1]
            return last_line.split(" ", 1)[1].strip()

    def log(self):
        self.timer.start(10*60*1000)
        self.timer.timeout.connect(self.update_log)

    def stop_log(self):
        self.timer.stop()

    def update_log(self):
        self.folder = self.dev_nb['folder']
        self.log_dir = str(Path(self.folder).parents[0])
        self.log_file = os.path.join(self.log_dir, 'log.txt')

        self.t_start_eastern = time.time() - (60.0 * 60.0 * 5.0) # convert from UTC to Eastern time (-4hrs)
        self.now = datetime.datetime.utcfromtimestamp(float(self.t_start_eastern))
        self.dt_string = self.now.strftime('%m-%d-%y_%H:%M:%S')

        with open(self.log_file, "a") as f:
            f.write("{}".format(self.dt_string) + "\n")

        with open(self.log_file, "a") as f:
            for port in self.ports:
                f.write("Port {}: ".format(port))
                f.write("\n")
                for sensor in self.sensors:
                    if self.last_value_search(port, sensor) is not None:
                        f.write("{}: {}".format(sensor, self.last_value_search(port, sensor)) + "\n")
                f.write("\n")

        self.folder = self.dev_sens['folder']
        with open(self.log_file, "a") as f:
            for iomport in self.iomports:
                f.write("Iomport {}: ".format(iomport))
                for chan in self.in_chans:
                    if self.last_value_search(iomport, chan) is not None:
                        f.write("Chan {}: {} ".format(chan, self.last_value_search(iomport, chan)))
                f.write("\n")

        with open(self.log_file, "a") as f:
            f.write("========================================================" + "\n")

