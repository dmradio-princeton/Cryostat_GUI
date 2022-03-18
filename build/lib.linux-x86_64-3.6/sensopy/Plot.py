from PyQt5 import QtWidgets, QtCore
from Data import Data

import datetime, time, sys, os, re
import numpy as np
import pyqtgraph as pg

import matplotlib.pyplot as plt

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

#for pyinstaller:
#import pkg_resources.py2_warn

class Plot:
    def __init__(self, dev):
        
        self.dev = dev
        self.data = dev['data']
        self.folder = dev['folder']
        self.ports = dev['ports']
        self.sensors = dev['sensors']
        self.label = dev['label']
        self.units = dev['units']
        self.time = dev['time']

        #Creating temporary data array for plotting
        self.temp_data = {}
        for port in self.ports:
            self.temp_data[port] = {}
            for sensor in self.sensors:
                self.temp_data[port][sensor] = np.empty((0, 2))

        self.timer = QtCore.QTimer()

        self._widgets()
        self._layout()

    def _widgets(self):
        self.plot = {}
        for port in self.ports:
             self.current_port = re.search(r'\d+', str(port)).group()
             self.plot[port] = SimplePlotWidget()
             self.plot[port].set_title('Port ' + self.current_port)
             self.plot[port].set_ylabel(self.label, self.units)
             self.plot[port].legend()
             self.plot[port].grid()
             for sensor in self.sensors:
                 self.curve = "{}".format(sensor)
                 self.plot[port].add_curve(self.curve)

        self.start_button = QtWidgets.QPushButton('Start/continue plot')
        self.start_button.clicked.connect(self.start_plotting)

        self.refresh_button = QtWidgets.QPushButton('Refresh plot')
        self.refresh_button.clicked.connect(self.refresh_plotting)

        self.allltime_button = QtWidgets.QPushButton('All time plot')
        self.allltime_button.clicked.connect(self.alltime_plotting)

        self.folder_line = QtWidgets.QLineEdit("")
        self.folder_line.setText(self.folder)

        self.stop_button = QtWidgets.QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_plotting)

     #   if self.label == 'Magnetic Field':
     #       self.frequency_label= QtWidgets.QLabel("Frequency (Hz):")
     #       self.duration_label= QtWidgets.QLabel("Duration (s):")
     #       self.sampling_rate_label= QtWidgets.QLabel("Sampling rate  (samples/s):")

     #       self.x_coord_label= QtWidgets.QLabel("x:")
     #       self.y_coord_label= QtWidgets.QLabel("y:")
     #       self.z_coord_label= QtWidgets.QLabel("z:")


     #       self.frequency = QtWidgets.QLineEdit("")
     #       self.duration = QtWidgets.QLineEdit("90")
     #       self.sampling_rate = QtWidgets.QLineEdit("250")

     #       self.x_coord = QtWidgets.QLineEdit("0")
     #       self.y_coord = QtWidgets.QLineEdit("0")
     #       self.z_coord = QtWidgets.QLineEdit("0")

     #       self.measure_button = QtWidgets.QPushButton('Measure')  
     #       self.measure_button.clicked.connect(self.measure)    


    def _layout(self):
        self.grid_plot = QtWidgets.QGridLayout()
        i = 0
        for port in self.ports:
            self.grid_plot.addWidget(self.plot[port], i, 0, 1 , 3)
            i += 1

        self.grid_plot.addWidget(self.start_button, i, 0)
        self.grid_plot.addWidget(self.refresh_button, i, 1)
        self.grid_plot.addWidget(self.allltime_button, i , 2)

        self.grid_plot.addWidget(self.folder_line, i + 1 , 0 , 1 , 3)
        self.grid_plot.addWidget(self.stop_button, i + 2 , 0 , 1 , 3)

     #   if self.label == 'Magnetic Field':
     #       self.groupBox_measure = QtWidgets.QGroupBox("Measurements")
     #       self.grid_measure = QtWidgets.QGridLayout()

     #       self.grid_measure.addWidget(self.frequency_label, 0 , 0 , 1 , 1)
     #       self.grid_measure.addWidget(self.frequency, 0 , 1 , 1 , 1)

     #       self.grid_measure.addWidget(self.duration_label, 0 , 2 , 1 , 1)
     #       self.grid_measure.addWidget(self.duration , 0 , 3 , 1 , 1)

     #       self.grid_measure.addWidget(self.sampling_rate_label, 0 , 4 , 1 , 1)
     #       self.grid_measure.addWidget(self.sampling_rate, 0 , 5 , 1 , 1)

     #       self.grid_measure.addWidget(self.x_coord_label, 1 , 0 , 1 , 1)
     #       self.grid_measure.addWidget(self.x_coord, 1 , 1 , 1 , 1)

     #       self.grid_measure.addWidget(self.y_coord_label, 1 , 2 , 1 , 1)
     #       self.grid_measure.addWidget(self.y_coord , 1 , 3 , 1 , 1)

     #       self.grid_measure.addWidget(self.z_coord_label, 1 , 4 , 1 , 1)
     #       self.grid_measure.addWidget(self.z_coord, 1 , 5 , 1 , 1)

     #       self.grid_measure.addWidget(self.measure_button, 2 , 0 , 1 , 6)

     #       self.groupBox_measure.setLayout(self.grid_measure)

     #       self.grid_plot.addWidget(self.groupBox_measure, i + 3 , 0 , 1 , 3)


    def start_plotting(self):
        self.timer.stop()
        self.timer.start(self.time)
        self.timer.timeout.connect(self.update_plot)

    def measure(self):
        self.timer.stop()

        FREQ = self.frequency.text()
        DURATION = float(self.duration.text())
        USER_SAMPLE_RATE = float(self.sampling_rate.text())
        COORD = '[x={}:y={}z={}:]'.format(self.x_coord.text(),self.y_coord.text(),self.z_coord.text())

        self.data[15].make_measurement(FREQ,DURATION,USER_SAMPLE_RATE,COORD)

        self.timer.start(self.time)
        self.timer.timeout.connect(self.alltime_plot)

    def refresh_plotting(self):
        self.timer.stop()
        for port in self.ports:
            for sensor in self.sensors:
                self.temp_data[port][sensor] = np.empty((0, 2))
        self.timer.start(self.time)
        self.timer.timeout.connect(self.update_plot)

    def stop_plotting(self):
        self.timer.stop()

    def alltime_plotting(self):
        self.timer.stop()
        self.timer.start(self.time)
        self.timer.timeout.connect(self.alltime_plot)

    def update_plot(self):
        for port in self.ports:
            self.Data = Data(self.dev, port)
            for sensor in self.sensors:
                self.Data.process_data(sensor)

                #Empty data to free memory
                if np.shape(self.temp_data[port][sensor])[0] > 2000:
                    self.temp_data[port][sensor] = np.empty((0, 2))

                self.new_data = np.array([[self.Data.t, self.Data.reading]])
                self.temp_data[port][sensor] = np.append(self.temp_data[port][sensor], self.new_data , axis=0)
                self.plot[port].set_data(self.Data.curve, self.temp_data[port][sensor])

    def alltime_plot(self):
        for port in self.ports:
            self.Data = Data(self.dev, port)
            for sensor in self.sensors:
                self.Data.process_data(sensor)

                self.plot_data = np.loadtxt(self.Data.file_path)

                #If it's the first measurement, need to reshape from list to matrix
                if self.plot_data.ndim == 1:
                    self.plot_data = self.plot_data.reshape(1,2)

                self.plot_data[:,0] = [x + self.Data.time_stamps[port][sensor] for x in self.plot_data[:,0]]
                self.plot[port].set_data(self.Data.curve, self.plot_data)


class SimplePlotWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.curves = {}
        self.pens = iter([pg.mkPen(color='#1b9e77', width=2),
                     pg.mkPen(color='#d95f02', width=2),
                     pg.mkPen(color='#7570b3', width=2),
                     pg.mkPen(color='#e7298a', width=2),
                     pg.mkPen(color='#66a61e', width=2),
                     pg.mkPen(color='#e6ab02', width=2),
                     pg.mkPen(color='#a6761d', width=2),
                     pg.mkPen(color='#666666', width=2)])

        self._plot()
        self._layout()

    def _plot(self):
        self.pg = pg.GraphicsLayoutWidget()
        self.plt = self.pg.addPlot(row=1, col=1, title='',
                                     axisItems={'bottom': TimeAxisItem(orientation='bottom')})
        self.plt.setMenuEnabled(enableMenu=True)
        #self.plt.setYRange(260, 300, padding=0)

    def _layout(self):
        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addWidget(self.pg)
        self.setLayout(self.vbox)

    def add_curve(self, crv_name):
        #if crv_name == '6':
        #    self.curves[crv_name] = (self.plt.plot(name='Generator'))
        #    self.curves[crv_name].setPen(next(self.pens))
        #if crv_name == '5':
        #    self.curves[crv_name] = (self.plt.plot(name='3-axis'))
        #    self.curves[crv_name].setPen(next(self.pens))
        #if crv_name == '7':
        #    self.curves[crv_name] = (self.plt.plot(name='1-axis'))
        #    self.curves[crv_name].setPen(next(self.pens))

        self.curves[crv_name] = (self.plt.plot(name=crv_name))
        self.curves[crv_name].setPen(next(self.pens))

    def set_title(self, title):
        self.plt.setTitle(title)

    def set_ylabel(self, label, units=None):
        self.plt.setLabel('left', label, units)

    def grid(self, x=True, y=True):
        self.plt.showGrid(x=x, y=y)

    def legend(self):
        self.plt.addLegend()

    @QtCore.pyqtSlot()
    def set_data(self, crv_name, data):

        # if data.shape[0] > 1:
        self.curves[crv_name].setData(data[:, 0], data[:, 1])


class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        return [self.int2dt(value).strftime("%m/%d/%y\n%H:%M:%S") for value in values]

    def int2dt(self, ts):
        ts = ts - (60.0 * 5.0 * 60.0)  # convert from UTC to Eastern time (-5hrs)
        return datetime.datetime.utcfromtimestamp(float(ts))
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Plots()
    window.show()
    sys.exit(app.exec_())
