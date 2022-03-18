#!/usr/bin/env python3
from Sens import Sensoray
from Sens import S2608
from Nb import Nb
from Agilent import instrument
from Main import Measurement

from NormBoxReadings import NormBoxReadings
from SensorayReadings import SensorayReadings
from SignalGenerator import SignalGenerator
from HeCycle import HeCycle

from Plot import Plot
from Search import Search
from Data import Data

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSlot

import datetime
import time
import sys, os

#for pyinstaller:
#import pkg_resources.py2_warn

folder = ''

class StartWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.title = 'Welocme to DMRadio at Princeton!'

        self.left = 0
        self.top = 0
        self.width = 500
        self.height = 100

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)

        self._widgets()
        self._layout()

    def _widgets(self):
        self.create_folder_button = QtWidgets.QPushButton('Start new cooldown')
        self.open_folder_button = QtWidgets.QPushButton('Choose directory')
        self.confirm_button = QtWidgets.QPushButton('Confirm')
        self.folder_line = QtWidgets.QLineEdit('')

        self.create_folder_button.clicked.connect(self.create_cooldown_folder)
        self.open_folder_button.clicked.connect(self.open_cooldown_folder)
        self.confirm_button.clicked.connect(self.confirm)

        self.checkbox = QtWidgets.QCheckBox('Use Waveform Generator')

        self.NotMeasureMag = QtWidgets.QCheckBox("Don't measure B-field")
        self.MeasureMagCooling = QtWidgets.QCheckBox("Measure: cooling down")
        self.MeasureMagWarming = QtWidgets.QCheckBox("Measure: warming up")

        self.NotMeasureMag.setChecked(True)
        self.NotMeasureMag.stateChanged.connect(self.onStateChange)
        self.MeasureMagCooling.stateChanged.connect(self.onStateChange)
        self.MeasureMagWarming.stateChanged.connect(self.onStateChange)

        global checkbox, NotMeasureMag, MeasureMagCooling, MeasureMagWarming
        checkbox = self.checkbox
        NotMeasureMag = self.NotMeasureMag
        MeasureMagCooling = self.MeasureMagCooling
        MeasureMagWarming = self.MeasureMagWarming

    def _layout(self):
        self.grid = QtWidgets.QGridLayout()
        self.grid.addWidget(self.create_folder_button, 0, 0, 1, 3)
        self.grid.addWidget(self.open_folder_button, 1, 0, 1, 3)
        self.grid.addWidget(self.folder_line, 2, 0, 1, 3)
        self.grid.addWidget(self.confirm_button, 3, 0, 1, 3)
        self.grid.addWidget(self.checkbox, 4, 0, 1, 3)
        self.grid.addWidget(self.NotMeasureMag, 5, 0)
        self.grid.addWidget(self.MeasureMagCooling, 5, 1)
        self.grid.addWidget(self.MeasureMagWarming, 5, 2)

        self.central_widget.setLayout(self.grid)

    def create_cooldown_folder(self):
        t_start_eastern = time.time() - (60.0 * 60.0 * 5.0) # convert from UTC to Eastern time (-4hrs)
        now = datetime.datetime.utcfromtimestamp(float(t_start_eastern))
        dt_string = now.strftime('%m-%d-%y_%H:%M:%S')

        self.folder = '/home/dmradio/Documents/cryostat_data/' + dt_string
        self.folder_line.setText(self.folder)

        global folder
        folder = self.folder

        os.makedirs(self.folder)
        print('{} is created'.format(self.folder))

    def open_cooldown_folder(self):
        self.folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, 'Choose Directory',
'/home/dmradio/Documents/cryostat_data'))
        self.folder_line.setText(self.folder)

        global folder
        folder = self.folder
        print('{} is open'.format(self.folder))

    def confirm(self):
        self.main = MainWindow()
        self.main.display()
        self.close()

    @pyqtSlot(int)
    def onStateChange(self, state):
        if state == Qt.Checked:
            if self.sender() == self.NotMeasureMag:
                self.MeasureMagCooling.setChecked(False)
                self.MeasureMagWarming.setChecked(False)
            elif self.sender() == self.MeasureMagCooling:
                self.NotMeasureMag.setChecked(False)
                self.MeasureMagWarming.setChecked(False)
            elif self.sender() == self.MeasureMagWarming:
                self.NotMeasureMag.setChecked(False)
                self.MeasureMagCooling.setChecked(False)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.title = 'DMRadio at Princeton. Cryostat Control Panel v 1.0'

        self.left = 0
        self.top = 0
        self.width = 1200
        self.height = 600

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)

    def display(self):
        self.show()

class MyTableWidget(QtWidgets.QTabWidget):

    def __init__(self, parent):
        super(MyTableWidget, self).__init__(parent)

        self.ip_adress = '10.10.10.1'
        self.iomports =  [7, 15]
        self.in_chans = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        self.out_chans = [0, 1, 2, 3, 4, 5, 6, 7]

        self.nb_ports = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyUSB2"]
        self.sensors = ["D1", "D2", "D3", "D4", "D5", "R1", "R2", "R3"]

        print('Connecting to Sensoray MM, IP adress: {}...'.format(self.ip_adress))
        self.sens = Sensoray(self.ip_adress)

        print('Initializing Sensoray 2608...')
        self.sens2608 = {}
        for iomport in self.iomports:
            self.sens2608[iomport] = S2608(iomport)

        print('Initializing Norms Boxes...')
        self.nb = {}
        for port in self.nb_ports:
            self.nb[port] = Nb(port, self.sensors)

        if checkbox.isChecked():
            self.agilent = instrument("/dev/usbtmc0")

        self.dev = {}
        self.mag_temp_isfound = False

        self.dev['norm_box'] = {
                            'data': self.nb,
                            'folder': os.path.join(folder,"norm_boxes"),
                            'ports': self.nb_ports,
                            'sensors': self.sensors}

        self.dev['diodes'] = {
                            'data': self.nb,
                            'folder': os.path.join(folder,"norm_boxes"),
                            'ports': self.nb_ports,
                            'sensors': ["D1", "D2", "D3", "D4", "D5"],
                            'label': 'Temperature',
                            'units': 'K',
                            'time': 30000}
                            #'time': 1000}

        self.dev['ruoxes'] = {
                            'data': self.nb,
                            'folder': os.path.join(folder,"norm_boxes"),
                            'ports': self.nb_ports,
                            'sensors':  ["R1", "R2", "R3"],
                            'label': 'Resistance',
                            'units': '\u03A9',
                            'time': 30000}

        self.dev['sensoray'] = {
                            'data': self.sens2608,
                            'folder': os.path.join(folder,"sensoray"),
                            'ports': self.iomports,
                            'sensors': self.in_chans,
                            'out_chans': self.out_chans}


        self.dev['sens_temp'] = {
                            'data': self.sens2608,
                            'folder': os.path.join(folder,"sensoray"),
                            'ports': [7],
                            'sensors':  [8, 10, 11, 12],
                            'label': 'Temperature',
                            'units': 'K',
                            'time': 1000}

        self.dev['sens_press'] = {
                            'data': self.sens2608,
                            'folder': os.path.join(folder,"sensoray"),
                            'ports': [7],
                            'sensors':  [6],
                            'label': 'Pressure',
                            'units': 'Torr',
                            'time': 1000}

        self.dev['sens_magnet'] = {
                            'data': self.sens2608,
                            'folder': os.path.join(folder,"sensoray"),
                            'ports': [15],
                            #'sensors':  [6,4,5,7,10],
                            #'sensors':  [6,7,10],
                            #'sensors':  [6,7,5],
                            'sensors':  [6,7],
                            'label': 'Magnetic Field',
                            'units': 'V',
                            'time': 0.001}

        self.dev['sens_transducers'] = {
                            'data': self.sens2608,
                            'folder': os.path.join(folder,"sensoray"),
                            'ports': [15],
                            'sensors':  [2,3,14,15],
                            'label': 'Transducers',
                            'units': 'K',
                            'time': 1000}
        if checkbox.isChecked():
            self.dev['agilent'] = {
                            'data': self.agilent,
                            'folder': os.path.join(folder,"agilent")}


        self.NormBoxReadings = NormBoxReadings(self.dev['norm_box'])
        self.SensorayReadings = SensorayReadings(self.dev['sensoray'])

        self.Search = Search(self.dev['norm_box'], self.dev['sensoray'])
       # self.Search = Search(self.dev['norm_box'])

        if checkbox.isChecked():
            self.SignalGenerator = SignalGenerator(self.dev['agilent'])

        self.NormBoxDiodes = Plot(self.dev['diodes'])
        self.NormBoxRuoxes = Plot(self.dev['ruoxes'])

        self.SensorayTemperature = Plot(self.dev['sens_temp'])
        self.SensorayPressure = Plot(self.dev['sens_press'])
        self.SensorayMagnet = Plot(self.dev['sens_magnet'])

        self.HeCycle = HeCycle(self.dev['norm_box'], self.dev['sensoray'])


        # Initialize tab screen
        self.tab1 = QtWidgets.QWidget()
        self.tab2 = QtWidgets.QWidget()
        self.tab3 = QtWidgets.QWidget()
        self.tab4 = QtWidgets.QWidget()
        if checkbox.isChecked():
             self.tab5 = QtWidgets.QWidget()
        self.tab6 = QtWidgets.QWidget()
        self.tab7 = QtWidgets.QWidget()
        self.tab8 = QtWidgets.QWidget()
        self.tab9 = QtWidgets.QWidget()
        self.tab10 = QtWidgets.QWidget()

        # Add tabs
        self.addTab(self.tab1,"Norm Boxes")
        self.addTab(self.tab2,"Norm Boxes Diodes")
        self.addTab(self.tab3,"Norm Boxes RuOxes")
        self.addTab(self.tab4,"Sensoray")

        if checkbox.isChecked():
            self.addTab(self.tab5,"Signal Generator")

        self.addTab(self.tab6,"Sensoray Temperature")
        self.addTab(self.tab7,"Sensoray Pressure")
        self.addTab(self.tab8,"Sensoray Magnetic Field")
        self.addTab(self.tab9,"Search")
        self.addTab(self.tab10,"He cycle")

        # Create first tab
        self.tab1.setLayout(self.NormBoxReadings.grid)
        self.tab2.setLayout(self.NormBoxDiodes.grid_plot)
        self.tab3.setLayout(self.NormBoxRuoxes.grid_plot)
        self.tab4.setLayout(self.SensorayReadings.grid)

        if checkbox.isChecked():
            self.tab5.setLayout(self.SignalGenerator.grid)

        self.tab6.setLayout(self.SensorayTemperature.grid_plot)
        self.tab7.setLayout(self.SensorayPressure.grid_plot)
        self.tab8.setLayout(self.SensorayMagnet.grid_plot)
        self.tab9.setLayout(self.Search.grid)
        self.tab10.setLayout(self.HeCycle.vbox)


        if not(NotMeasureMag.isChecked()):
            print('Let\'s measure B-field!')
            self.timer = QtCore.QTimer()
            self.check_resplate_temperature()

    def check_resplate_temperature(self):
        self.timer.stop()
        self.timer.start(1000*60)
        self.timer.timeout.connect(self.get_resplate_temperature)

    def get_resplate_temperature(self):
        #measure the temperature of the resplate
        self.resplate_temp = Data(self.dev['sensoray'], 7)

        #channel 8 corresponds to resplate
        self.resplate_temp.process_data(8)

        if MeasureMagCooling.isChecked():
            self.mag_temps = [300,275,250,225,200,175,150,125,100,75,50,40,30,20,10,4]
            self.determine_temperature_cooling()

        if MeasureMagWarming.isChecked():
            self.mag_temps = [4,10,20,30,40,50,75,100,125,150,175,200,225,250,275,290]
            self.determine_temperature_warming()

    def determine_temperature_cooling(self):
        #If the program runs for the first time, find the next temperature the B-field
        if self.resplate_temp.reading > 4:
            if self.mag_temp_isfound == False:
                for mag_temp in self.mag_temps:
                    #search for the next temperature to measure the B-field
                    if self.resplate_temp.reading > mag_temp:
                        self.N_mag_temp = self.mag_temps.index(mag_temp)
                        print('Next B-field measurement will be at T={}K'.format(self.mag_temps[self.N_mag_temp]))

                        #will not search next time
                        self.mag_temp_isfound = True
                        break

            #measure the B-field once the temperature reached the required value
            if float(self.resplate_temp.reading) < self.mag_temps[self.N_mag_temp]:
                self.stop_plotting()
                self.measure_Bfield()
                self.continue_plotting()

    def determine_temperature_warming(self):
        #If the program runs for the first time, find the next temperature the B-field
        if self.resplate_temp.reading < 300:
            if self.mag_temp_isfound == False:
                for mag_temp in self.mag_temps:
                    #search for the next temperature to measure the B-field
                    if self.resplate_temp.reading < mag_temp:
                        self.N_mag_temp = self.mag_temps.index(mag_temp)
                        sys.stdout.write('Next B-field measurement will be at T={}K'.format(self.mag_temps[self.N_mag_temp]))

                        #will not search next time
                        self.mag_temp_isfound = True
                        break

            #measure the B-field once the temperature reached the required value
            if float(self.resplate_temp.reading) > self.mag_temps[self.N_mag_temp]:
                self.stop_plotting()
                self.measure_Bfield()
                self.continue_plotting()

    def stop_plotting(self):
        #stop plotting
        self.NormBoxDiodes.stop_plotting()
        self.NormBoxRuoxes.stop_plotting()
        self.SensorayTemperature.stop_plotting()
        self.SensorayPressure.stop_plotting()
        self.SensorayMagnet.stop_plotting()

    def measure_Bfield(self):
        #start measuring the B-field
        temp = self.resplate_temp.reading
        sys.stdout.write('B-field measurement at T={:.0f}K'.format(temp))
        NAME = os.path.join(os.path.join(folder,'Bfield'),'Cold_measurement_X200AMP_1_' + '{:.0f}'.format(temp) + 'K')
        Measurement(NAME, Data(self.dev['sensoray'], 15))
        self.N_mag_temp += 1

    def continue_plotting(self):
        #continue plotting
        self.NormBoxDiodes.start_plotting()
        self.SensorayTemperature.start_plotting()
        self.SensorayPressure.start_plotting()

        sys.stdout.write('Next B-field measurement will be at T={}K'.format(self.mag_temps[self.N_mag_temp]))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    sw = StartWindow()
    sw.show()
    sys.exit(app.exec_())
