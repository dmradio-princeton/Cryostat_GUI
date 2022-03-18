import time, os, re
import numpy as np
import pandas as pd

import datetime
from collections import namedtuple

Pair = namedtuple("Pair", ["t", "v"])
#pairs = [Pair(400.0, 0.27456), Pair(300.0, 0.51892), Pair(24.0, 1.13698), Pair(10.0, 1.42014), Pair(1.4,1.69812), Pair(1.0,1.80)]
pairs_dt470 =\
[Pair(400.0, 0.27456),\
Pair(350.0, 0.39783),\
Pair(300.0, 0.51892),\
Pair(250.0, 0.63841),\
Pair(200.0, 0.75554),\
Pair(150.0, 0.86873),\
Pair(100.0, 0.97550),\
Pair(90.0, 0.99565),\
Pair(80.0, 1.01525),\
Pair(70.0, 1.03425),\
Pair(60.0, 1.05267),\
Pair(50.0, 1.07053),\
Pair(40.0, 1.08781),\
Pair(30.0, 1.10702),\
Pair(24.0, 1.13598),\
Pair(20.0, 1.21440),\
Pair(10.0, 1.42013),\
Pair(9.0, 1.45048),\
Pair(8.0, 1.48443),\
Pair(7.0, 1.52166),\
Pair(6.0, 1.56027),\
Pair(5.0, 1.59782),\
Pair(4.0, 1.63263),\
Pair(3.0, 1.66292),\
Pair(2.0, 1.68786),\
Pair(1.4, 1.69812),\
Pair(1.0, 1.42014)]

pairs_dt670 =\
[Pair(400.0, 0.325839),\
Pair(350.0, 0.443371),\
Pair(300.0, 0.559639),\
Pair(250.0, 0.673462),\
Pair(200.0, 0.783720),\
Pair(150.0, 0.889114),\
Pair(100.0, 0.986974),\
Pair(90.0, 1.005244),\
Pair(80.0, 1.022984),\
Pair(70.0, 1.040183),\
Pair(60.0, 1.056862),\
Pair(50.0, 1.073099),\
Pair(40.0, 1.089024),\
Pair(30.0, 1.106244),\
Pair(24.0, 1.125923),\
Pair(20.0, 1.197748),\
Pair(10.0, 1.38373),\
Pair(9.0, 1.41207),\
Pair(8.0, 1.44374),\
Pair(7.0, 1.47868),\
Pair(6.0, 1.51541),\
Pair(5.0, 1.55145),\
Pair(4.0, 1.58465),\
Pair(3.0, 1.612000),\
Pair(2.0, 1.634720),\
Pair(1.4, 1.644290)]

pairs_d61111617 =\
[Pair(330.155044930712, 0.48445),\
Pair(326.140017861239, 0.49386),\
Pair(320.146127408098, 0.50789),\
Pair(315.146283712057, 0.51957),\
Pair(305.120849779077, 0.54293),\
Pair(290.117018354702, 0.57773),\
Pair(275.098778980911, 0.61232),\
Pair(260.079509635367, 0.64664),\
Pair(245.072488652325, 0.68063),\
Pair(230.071845149832, 0.71429),\
Pair(215.063245833382, 0.7476),\
Pair(200.061245658838, 0.78051),\
Pair(185.063951177578, 0.81298),\
Pair(170.057404279517, 0.84499),\
Pair(155.043968710798, 0.87648),\
Pair(140.046623925096, 0.90732),\
Pair(125.04167548054, 0.93746),\
Pair(110.057071271128, 0.96671),\
Pair(100.053173594297, 0.98569),\
Pair(94.057232390297, 0.99683),\
Pair(88.0661173342597, 1.00777),\
Pair(82.0540607103976, 1.01856),\
Pair(76.0614649532858, 1.0291),\
Pair(70.0685491252497, 1.03944),\
Pair(64.0672459653141, 1.04959),\
Pair(58.0734502763796, 1.05954),\
Pair(52.0731930614762, 1.06933),\
Pair(46.0728018939668, 1.079),\
Pair(42.0864102495046, 1.08536),\
Pair(38.0987107348207, 1.09177),\
Pair(35.1041838821919, 1.09676),\
Pair(32.1011579006054, 1.10205),\
Pair(30.0725420580562, 1.10587),\
Pair(29.0551692129, 1.10792),\
Pair(28.0455272053147, 1.11009),\
Pair(27.2335878464234, 1.112),\
Pair(26.4216414828489, 1.11415),\
Pair(25.6170983731766, 1.11667),\
Pair(25.0117003251323, 1.11906),\
Pair(24.4141117273344, 1.12224),\
Pair(23.8153994672332, 1.1272),\
Pair(23.2178667533883, 1.13554),\
Pair(22.6240856164454, 1.1476),\
Pair(21.8288715253763, 1.16494),\
Pair(21.0380416083584, 1.17957),\
Pair(20.0539082855541, 1.19555),\
Pair(19.0733140980097, 1.2106),\
Pair(18.0980471637337, 1.22542),\
Pair(17.1301513785744, 1.24033),\
Pair(16.1439183116825, 1.25602),\
Pair(15.1647680259477, 1.27241),\
Pair(14.1736115918337, 1.29003),\
Pair(13.1769219563201, 1.30914),\
Pair(12.1706067451424, 1.33008),\
Pair(11.1582302197905, 1.35303),\
Pair(10.1303242869574, 1.37854),\
Pair(9.11206974377479, 1.40645),\
Pair(8.09931768466379, 1.43732),\
Pair(7.00644302335852, 1.47398),\
Pair(6.02336367854162, 1.50856),\
Pair(5.01106449812682, 1.54352),\
Pair(4.18875383837627, 1.56993),\
Pair(3.68835330134253, 1.58417),\
Pair(3.1978459704497, 1.59671),\
Pair(2.79749618203169, 1.6063),\
Pair(2.39618560851893, 1.61542),\
Pair(2.00246428004826, 1.62353),\
Pair(1.70169804045155, 1.62883),\
Pair(1.40040144112562, 1.63314),\
Pair(1.30330991104416, 1.63429),\
Pair(1.19980671042335, 1.63538)]

#for pyinstaller:
#import pkg_resources.py2_warn

class Data:
    def __init__(self, dev, port):
        self.folder = dev['folder']
        self.ports = dev['ports']
        self.sensors = dev['sensors']

        self.port = port

        #Figure out if it's Norm's box or Sensoray
        if isinstance(self.port, str):
            self.data = dev['data'][port].handle_Q()
        else:
            self.data = dev['data'][port]

        #Check if dictionary of time stamps exists
        try: self.time_stamps
        except AttributeError: self.time_stamps = None

        #If not initializing dictionary for time stamps
        if self.time_stamps is None:
            self.time_stamps = {}
            for port in self.ports:
                self.time_stamps[port] = {}
                for sensor in self.sensors:
                    self.time_stamps[port][sensor] = 0

    def process_data(self, sensor):
        self.curve = "{}".format(sensor)
        self.t = time.time()

        t_output = datetime.datetime.utcfromtimestamp(float(self.t - (60.0 * 60.0 * 4.0))).strftime("%m/%d/%y\n%H:%M:%S")

        self.get_reading(sensor)
        
        self.reading = self.meas    
        self.current_port = re.search(r'\d+', str(self.port)).group()

        self.dir_path = os.path.join(self.folder, self.current_port)
        self.file_path = os.path.join(self.dir_path, self.curve + ".dat")
        self.file_path_full = os.path.join(self.dir_path, self.curve + ".txt")
        self.file_path_csv = os.path.join(self.dir_path, self.curve + ".csv")

        self.ts_dir_path = os.path.join(self.dir_path, "time_stamp")
        self.ts_file_path = os.path.join(self.ts_dir_path, self.curve + "_time_stamp" + ".dat")


        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
            os.makedirs(self.ts_dir_path)

            columns = ['Date', 'Temperature [K]']
            data_frame = pd.DataFrame(np.array([[t_output, self.reading]]))
            data_frame.to_csv(self.file_path_csv, header = columns, index=False)

        #Check if time stamp exists and create it if not
        if self.time_stamps[self.port][sensor] == 0:
            with open(self.ts_file_path, "a") as f:
                if f.tell() == 0:
                   f.write(str(self.t))

            #Read the time stamp
            with open(self.ts_file_path) as f:
                self.time_stamps[self.port][sensor] = float(f.readline())

        #Write the data into the file with time elapsed from the time stamp
        with open(self.file_path, "a") as f:
            np.savetxt(f, np.array([[self.t-self.time_stamps[self.port][sensor], self.reading]]), newline="\n", fmt='%1.3f')
        with open(self.file_path_full, "a") as f:
            f.write("{} {}".format(self.t,self.line) + "\n")

        data_frame = pd.DataFrame(np.array([[t_output, self.reading]]))
        data_frame.to_csv(self.file_path_csv, mode='a', header=False, index=False)

    def get_reading_magfield(self):
        return np.array([self.data.get_2ains_magnet(6,7)])

    def get_reading(self, sensor):
	#Check if reading corresponds to Sensoray or Norm Box (Norm Box port is written as a string)
        if isinstance(self.port, str):
            self.read = self.data[sensor].rsplit(' ')
            if sensor[0] == 'D':
                if (1 <= int(sensor[1])) and (int(sensor[1]) <= 3):
                    if int(sensor[1]) == 1:
                        self.meas = self.v_to_t_dt670(float(self.read[1][5:]))
                    else:
                        self.meas = self.v_to_t_dt470(float(self.read[1][5:]))

                    #self.read[2] is just an empty space, so we skip it
                    self.sp = self.read[3][3:]
                    self.p = self.read[4][2:]
                    self.i = self.read[5][2:]
                    self.h = self.read[6][2:]
                    self.line = "{:.2f} K, SP:{}, P:{}, I:{}, H:{}".format(self.meas,self.sp,self.p,self.i,self.h)
                else:
                    if (int(sensor[1]) == 4) and (self.port == "/dev/ttyUSB2"): #NB3D4 calibrated dioide
                        self.meas = self.v_to_t_d61111617(float(self.read[1][5:]))
                    else:
                        self.meas = self.v_to_t_dt470(float(self.read[1][5:]))

                    self.line = "{:.2f} K".format(self.meas)
            if sensor[0] == 'R':
                try:
                    self.meas = float(self.read[1][5:])
                    self.line = "{:.2f} \u03A9".format(self.meas)
                except ValueError:
                    self.meas = 0
                    self.line = "{} \u03A9".format(self.read[1][5:])
                
        else:
            temperature_dt470 = [11]
            temperature_dt670 = [8,10,12]
            pressure = [6]
            transducer = [2,3,14,15]
            magnet = [6,7]
            if (sensor in temperature_dt470) and self.port == 7:
                self.meas = self.v_to_t_dt470(self.data.get_ains()[sensor])
                self.line = "{:.2f} K".format(self.v_to_t_dt470(self.data.get_ains()[sensor]))
            elif (sensor in temperature_dt670) and self.port == 7:
                self.meas = self.v_to_t_dt670(self.data.get_ains()[sensor])
                self.line = "{:.2f} K".format(self.v_to_t_dt670(self.data.get_ains()[sensor]))
            elif (sensor in pressure) and self.port == 7:
                self.meas = self.v_to_p(self.data.get_ains()[sensor])
                self.line = "{:.2f} Torr".format(self.v_to_p(self.data.get_ains()[sensor]))
            elif (sensor in transducer) and self.port == 15:
                self.meas = self.v_to_t_temp(self.data.get_ains()[sensor])
                self.line = "{:.2f} K".format(self.v_to_t_temp(self.data.get_ains()[sensor]))
            elif (sensor in magnet) and self.port == 15:
                if sensor == 6:
                    self.meas = float(self.data.get_ains()[sensor])/100
                    self.line = "{:.3f} V".format(self.data.get_ains()[sensor]/100)
                else:    
                    self.meas = float(self.data.get_ains()[sensor])
                    self.line = "{:.3f} V".format(self.data.get_ains()[sensor])
            else:
                self.meas = 0
                self.line = "None"

    def v_to_p(self, v):
        if (1.9 < v) and (v < 10.1):
            return float(10**(v-6))
        return 0

    def v_to_t_dt470(self, v):
        if (0.27456 < v) and (v < 1.80):
            for i in range(26):
                if (pairs_dt470[i].v < v) and (v < pairs_dt470[i+1].v):
                   return float(pairs_dt470[i].t+ ((pairs_dt470[i+1].t - pairs_dt470[i].t)/(pairs_dt470[i+1].v - pairs_dt470[i].v))*(v - pairs_dt470[i].v))
        return 0

    def v_to_t_dt670(self, v):
        if (0.325839 < v) and (v < 1.644290):
            for i in range(26):
                if (pairs_dt670[i].v < v) and (v < pairs_dt670[i+1].v):
                   return float(pairs_dt670[i].t+ ((pairs_dt670[i+1].t - pairs_dt670[i].t)/(pairs_dt670[i+1].v - pairs_dt670[i].v))*(v - pairs_dt670[i].v))
        return 0

    def v_to_t_d61111617(self, v):
        if (0.48445 < v) and (v < 1.63538):
            for i in range(71):
                if (pairs_d61111617[i].v < v) and (v < pairs_d61111617[i+1].v):
                   return float(pairs_d61111617[i].t+ ((pairs_d61111617[i+1].t - pairs_d61111617[i].t)/(pairs_d61111617[i+1].v - pairs_d61111617[i].v))*(v - pairs_d61111617[i].v))
        return 0

    def v_to_t_temp(self, v):
        if (1 < v) and (v < 3.5):
            #There is 7.8kOhm resistor at the output of the transducer.
            #The circuit is active low-pass filter with  the gain=1.27.
            #We calculate here the output current from the transducer I=U/R, where U is divided by the gain.
            #1 \mu A = 1 K
            return float((1000000*v)/(1.27*7800))
        return 0
