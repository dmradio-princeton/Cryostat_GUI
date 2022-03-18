import time, os, re
import numpy as np

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

        self.get_reading(sensor)
        
        self.reading = self.meas    
        self.current_port = re.search(r'\d+', str(self.port)).group()

        self.dir_path = os.path.join(self.folder, self.current_port)
        self.file_path = os.path.join(self.dir_path, self.curve + ".dat")
        self.file_path_full = os.path.join(self.dir_path, self.curve + ".txt")

        self.ts_dir_path = os.path.join(self.dir_path, "time_stamp")
        self.ts_file_path = os.path.join(self.ts_dir_path, self.curve + "_time_stamp" + ".dat")

        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)
            os.makedirs(self.ts_dir_path)

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

    def v_to_t_temp(self, v):
        if (1 < v) and (v < 3.5):
            #There is 7.8kOhm resistor at the output of the transducer.
            #The circuit is active low-pass filter with  the gain=1.27.
            #We calculate here the output current from the transducer I=U/R, where U is divided by the gain.
            #1 \mu A = 1 K
            return float((1000000*v)/(1.27*7800))
        return 0
