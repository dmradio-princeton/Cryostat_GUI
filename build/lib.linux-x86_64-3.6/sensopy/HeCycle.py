from PyQt5 import QtWidgets, QtCore
from Data import Data

from PyQt5.QtCore import QRunnable, Qt, QThreadPool

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from LedIndicatorWidget import *

import datetime, time, sys, logging

logging.basicConfig(format="%(message)s", level=logging.INFO)

class HeCycle(QMainWindow):
    def __init__(self, dev_nb, dev_sens):
        super(self.__class__, self).__init__()

        self.dev_nb = dev_nb
        self.data_nb = dev_nb['data']
        self.folder_nb = dev_nb['folder']
        self.ports_nb = dev_nb['ports']
        self.sensors_nb = dev_nb['sensors']

        self.dev_sens = dev_sens
        self.data_sens = dev_sens['data']
        self.folder_sens = dev_sens['folder']
        self.iomports_sens = dev_sens['ports']
        self.in_chans_sens = dev_sens['sensors']
        self.out_chans_sens = dev_sens['out_chans']

        self.pids = ["SP", "P", "I"]

        self._widgets()
        self._layout()
        self._connections()

    def _widgets(self):

        self.item = {}
        self.item_label = {}
        self.item_button = {}

        self.heating_hrs = {}
        self.heating_mins = {}

        self.heating_hrs_label = {}
        self.heating_mins_label = {}
 
        self.waiting_hrs = {}
        self.waiting_mins = {}

        self.waiting_hrs_label = {}
        self.waiting_mins_label = {}

        self.run_cycle_button = {}

        self.heating_timer = {}
        self.waiting_timer = {}
        self.pid_settings_line = {}

        self.led_heater = {}
        self.led_heat_switch = {}

        for port in self.ports_nb:
            self.item[port] = {}
            self.item_label[port] = {}

            for pid in self.pids:
                self.item[port][pid] = QtWidgets.QDoubleSpinBox()
                self.item_label[port][pid] = QtWidgets.QLabel(pid +":")
                self.item_label[port][pid] = QtWidgets.QLabel(pid +":")

                if pid == "SP":
                    self.item[port][pid].setRange(1, 5000)
                elif pid == "P":
                   self.item[port][pid].setRange(1, 100)
                elif pid == "I":
                    self.item[port][pid].setRange(0, 100)


            #set up heating time
            self.heating_hrs[port] = QtWidgets.QDoubleSpinBox()
            self.heating_mins[port] = QtWidgets.QDoubleSpinBox()

            self.heating_hrs_label[port] = QtWidgets.QLabel("hrs")
            self.heating_mins_label[port] = QtWidgets.QLabel("mins")

            self.heating_hrs[port].setRange(0, 5)
            self.heating_mins[port].setRange(0, 59)

            #set up waiting time
            self.waiting_hrs[port] = QtWidgets.QDoubleSpinBox()
            self.waiting_mins[port] = QtWidgets.QDoubleSpinBox()

            self.waiting_hrs_label[port] = QtWidgets.QLabel("hrs")
            self.waiting_mins_label[port] = QtWidgets.QLabel("mins")

            self.waiting_hrs[port].setRange(0, 5)
            self.waiting_mins[port].setRange(0, 59)

            self.heating_timer[port] = QtWidgets.QLineEdit("")
            self.waiting_timer[port] = QtWidgets.QLineEdit("")
            self.pid_settings_line[port] = QtWidgets.QLineEdit("")

            self.run_cycle_button[port] = QtWidgets.QPushButton('Run the cycle')

            self.led_heater[port] = LedIndicator(self)
            self.led_heater[port].setDisabled(True)  # Make the led non clickable

            self.led_heat_switch[port] = LedIndicator(self)
            self.led_heat_switch[port].setDisabled(True)  # Make the led non clickable

    def _layout(self):
        groupBox = {}
        gbox_port = {}

        groupBox_heat = {}
        groupBox_pid = {}
        groupBox_wait = {}

        heat_box = {}
        pid_box = {}
        wait_box = {}

        self.vbox = QtWidgets.QVBoxLayout()

        p = 0
        for port in self.ports_nb:
            if p == 0:
                groupBox[port] = QtWidgets.QGroupBox("3He cycle")
            else:
                groupBox[port] = QtWidgets.QGroupBox("4He" + str(p) + " cycle")
            gbox_port[port] = QtWidgets.QGridLayout()

            groupBox_pid[port] = QtWidgets.QGroupBox('Set PID for heating:')
            groupBox_heat[port] = QtWidgets.QGroupBox('Set heating time:')
            groupBox_wait[port] = QtWidgets.QGroupBox('Set waiting time:')

            heat_box[port] = QtWidgets.QGridLayout()
            pid_box[port] = QtWidgets.QGridLayout()
            wait_box[port] = QtWidgets.QGridLayout()

            r = 0
            for pid in self.pids:
                pid_box[port].addWidget(self.item_label[port][pid], r, 0)
                pid_box[port].addWidget(self.item[port][pid], r, 1)
                r += 1
            pid_box[port].addWidget(self.pid_settings_line[port], r, 0, 1, 2)
            groupBox_pid[port].setLayout(pid_box[port])

            heat_box[port].addWidget(self.heating_hrs[port], 0, 0)
            heat_box[port].addWidget(self.heating_hrs_label[port], 0, 1)
            heat_box[port].addWidget(self.heating_mins[port], 0, 2)
            heat_box[port].addWidget(self.heating_mins_label[port], 0, 3)
            heat_box[port].addWidget(self.heating_timer[port], 1, 0, 1 ,4)
            groupBox_heat[port].setLayout(heat_box[port])

            wait_box[port].addWidget(self.waiting_hrs[port], 0, 0)
            wait_box[port].addWidget(self.waiting_hrs_label[port], 0, 1)
            wait_box[port].addWidget(self.waiting_mins[port], 0, 2)
            wait_box[port].addWidget(self.waiting_mins_label[port], 0, 3)
            wait_box[port].addWidget(self.waiting_timer[port], 1, 0, 1 ,4)
            groupBox_wait[port].setLayout(wait_box[port])

            gbox_port[port].addWidget(groupBox_pid[port], 0, 0)
            gbox_port[port].addWidget(groupBox_heat[port], 0, 1)
            gbox_port[port].addWidget(groupBox_wait[port], 0, 2)
            gbox_port[port].addWidget(self.led_heater[port], 0, 3)
            gbox_port[port].addWidget(self.led_heat_switch[port], 0, 4)
            gbox_port[port].addWidget(self.run_cycle_button[port], 1, 0, 1, 3)

            groupBox[port].setLayout(gbox_port[port])

            self.vbox.addWidget(groupBox[port])

            p += 1
    def _connections(self):
        for port in self.ports_nb:
            self.run_cycle_button[port].clicked.connect(lambda checked, arg=port: self.run_cycle(arg))

    def run_cycle(self, port):
        pool = QThreadPool.globalInstance()

        sp = self.item[port]['SP'].value()
        p = self.item[port]['P'].value()
        i = self.item[port]['I'].value()

        heating_time = int(self.heating_hrs[port].value()*60*60 + self.heating_mins[port].value()*60)
        waiting_time = int(self.waiting_hrs[port].value()*60*60 + self.waiting_mins[port].value()*60)

     #   self.run_cycle_button[port].setEnabled(False)

        runnable = Runnable(
            self.dev_nb,
            self.dev_sens,
            port,
            sp,
            p,
            i,
            heating_time,
            waiting_time,
            self.run_cycle_button[port],
            self.heating_timer[port],
            self.waiting_timer[port],
            self.pid_settings_line[port],
            self.led_heater[port],
            self.led_heat_switch[port]
)
        pool.start(runnable)

class Runnable(QRunnable):
    def __init__(self, dev_nb, dev_sens, port, sp, p, i, heating_time, waiting_time, button, heating_timer, waiting_timer, pid_settings_line, led_heater, led_heat_switch):
        super().__init__()

        self.dev_nb = dev_nb
        self.data_nb = dev_nb['data']

        self.dev_sens = dev_sens
        self.data_sens = dev_sens['data']

        self.port = port
        self.sp = sp
        self.p = p
        self.i = i

        self.heating_time = heating_time
        self.waiting_time = waiting_time

        self.button = button

        self.heating_timer = heating_timer
        self.waiting_timer = waiting_timer

        self.pid_settings_line = pid_settings_line

        self.led_heater = led_heater
        self.led_heat_switch = led_heat_switch

    def run(self):
        sys.stdout.write("\n")

        self.turn_off_heat_switch(self.port)

        number = ''.join(filter(str.isdigit, self.port))
        if number == '0':
            label = f'3He'
        else:
            label = f'4He{number}'

        self.pid_settings_line.setText(f'Set SP={self.sp}')
        self.data_nb[self.port].handle_S('D1', self.sp)

        time.sleep(2)

        self.pid_settings_line.setText(f'Set P={self.p}')
        self.data_nb[self.port].handle_P('D1', self.p)

        time.sleep(2)

        self.pid_settings_line.setText(f'Set I={self.i}')
        self.data_nb[self.port].handle_I('D1', self.i)

        time.sleep(2)

        self.switch_heater_led()
        #self.data_nb[self.port].handle_H('D1', 1)

        self.pid_settings_line.setText("")

        for i in range(self.heating_time,0,-1):
            sys.stdout.write("\r")
            sys.stdout.write("Turn off heater in {}".format(datetime.timedelta(seconds=i)))
            self.heating_timer.setText("Turn off heater in {}".format(datetime.timedelta(seconds=i)))
            sys.stdout.flush()
            time.sleep(1)

        sys.stdout.write("\n")
        self.heating_timer.setText("")

        self.switch_heater_led()
        self.data_nb[self.port].handle_H('D1', 0)

        self.pid_settings_line.setText(f'Set SP=4.2')
        self.data_nb[self.port].handle_S('D1', 4.2)

        time.sleep(2)

        self.pid_settings_line.setText(f'Set P=100')
        self.data_nb[self.port].handle_P('D1', 100)

        time.sleep(2)

        self.pid_settings_line.setText(f'Set I=00')
        self.data_nb[self.port].handle_I('D1', 0)

        time.sleep(2)

        self.pid_settings_line.setText("")

        for i in range(self.waiting_time,0,-1):
            sys.stdout.write("\r")
            sys.stdout.write("Turn on HS in {}".format(datetime.timedelta(seconds=i)))
            self.waiting_timer.setText("Turn on HS in {}".format(datetime.timedelta(seconds=i)))
            sys.stdout.flush()
            time.sleep(1)

        sys.stdout.write("\n")
        self.waiting_timer.setText("")

        self.switch_heat_switch_led()
        self.turn_on_heat_switch(self.port)

        time.sleep(5)

        self.switch_heat_switch_led()
        self.turn_off_heat_switch(self.port)

        self.button.setEnabled(True)

    def switch_heater_led(self):
        self.led_heater.setChecked(not self.led_heater.isChecked())

    def switch_heat_switch_led(self):
        self.led_heat_switch.setChecked(not self.led_heat_switch.isChecked())

    def turn_on_heat_switch(self, port):
        if port == '/dev/ttyUSB0':
            self.data_sens[15].set_aout(1, 10)
            time.sleep(1)
            self.data_sens[15].set_aout(1, 0)
        elif port == '/dev/ttyUSB1':
            self.data_sens[15].set_aout(3, 10)
            time.sleep(1)
            self.data_sens[15].set_aout(3, 0)
        elif port == '/dev/ttyUSB2':
            self.data_sens[15].set_aout(5, 10)
            time.sleep(1)
            self.data_sens[15].set_aout(5, 0)

    def turn_off_heat_switch(self, port):
        if port == '/dev/ttyUSB0':
            self.data_sens[15].set_aout(0, 10)
            time.sleep(1)
            self.data_sens[15].set_aout(0, 0)
        elif port == '/dev/ttyUSB1':
            self.data_sens[15].set_aout(2, 10)
            time.sleep(1)
            self.data_sens[15].set_aout(2, 0)
        elif port == '/dev/ttyUSB2':
            self.data_sens[15].set_aout(4, 10)
            time.sleep(1)
            self.data_sens[15].set_aout(4, 0)
