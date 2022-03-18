/* Simple python extension that calls the sensoray API functions.
 * Author: Lucas Parker
 * E-mail: thelucasparker@gmail.com
 */
#include "sensopy.h"

static PyMethodDef sensopy_methods[] = {
	{"init_sensoray", init_sensoray, METH_VARARGS, "init_sensoray(ip_addr, mm_handle): initialize sensoray main module. ip_addr is string, mm_handle is optional. Returns a list of iomports where 2608 modules have been found."},
	{"reset_iom", reset_iom, METH_VARARGS, "reset_iom(iomport): resets the iom at given iomport."},
	{"get_2608_caldata", get_2608_caldata, METH_VARARGS, "get_2608_caldata(iomport): set/reset calibration data. Must be called at least once, before get_ains."},
	{"get_2608_aout", get_2608_aout, METH_VARARGS, "get_2608_aout(iomport, channel): return analog out reading."},
	{"set_2608_aout", set_2608_aout, METH_VARARGS, "set_2608_aout(iomport, channel, volts): set analog output value."},
	{"get_2608_ains", get_2608_ains, METH_VARARGS, "get_2608_ains(iomport): returns a list of 16 analog input values."},
	{"get_2608_ain", get_2608_ain, METH_VARARGS, "get_2608_ains(iomport): returns a list of 16 analog input values."},
	{"get_2608_2ains_magnet", get_2608_2ains_magnet, METH_VARARGS, "get_2608_ains(iomport): returns a list of 16 analog input values."},
	{"get_2608_4ains_magnet", get_2608_4ains_magnet, METH_VARARGS, "get_2608_ains(iomport): returns a list of 16 analog input values."},
	{"get_2608_5ains_magnet", get_2608_5ains_magnet, METH_VARARGS, "get_2608_ains(iomport): returns a list of 16 analog input values."},
	{"get_multiple_2608_ains", get_multiple_2608_ains, METH_VARARGS, "get_multiple_2608_ains(iomports): type(iomports) is list. Return dictionary of ains from those 2608's, keyed by their iomport number"},
	{"init_2608_ain_files", init_2608_ain_files, METH_VARARGS, "init_2608_ain_files(iomport): initialize struct, return PyCObject."},
	{"open_2608_ain_file", open_2608_ain_file, METH_VARARGS, "open_2608_ain_file(ain_files_cobject, fname, channel): Open a file for given channel's data."},
	{"write_2608_ains", write_2608_ains, METH_VARARGS, "write_2608_ains(ain_files_cobject): Sample 2608 ains and write to opened files."},
	{"flush_2608_ain_files", flush_2608_ain_files, METH_VARARGS, "flush_2608_ain_files(ain_files_cobject): flush ain files."},
	{"write_multiple_2608_ains", write_multiple_2608_ains, METH_VARARGS, "write_multiple_2608_ains(ain_files_cobject_list): Sample multiple 2608 ains and write to opened files."},
	{NULL, NULL}
};


static struct PyModuleDef _sensopy =
{
	PyModuleDef_HEAD_INIT,
	"_sensopy",
	"",
	-1,
	sensopy_methods
};

PyMODINIT_FUNC PyInit__sensopy(void) 
{
	return PyModule_Create(&_sensopy);
}

static PyObject *init_sensoray(PyObject *self, PyObject *args) {
	char *ip_addr;
	u8 iom_status[16];
	u16 nboards, iom_type[16];
	u32 faults;
	if (!PyArg_ParseTuple(args, "s", &ip_addr)) {
		fprintf(stderr, "(%s, %d): init_sensoray: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	// Initialize middleware, declaring only 1 mm board in system.
	if ((faults = S26_DriverOpen(1)) != 0) {
		fprintf(stderr, "(%s, %d): init_sensoray: DriverOpen() fault: %d.\n", __FILE__, __LINE__, faults);
		return NULL;
	}
	// Opem mm board.
	if ((faults = S26_BoardOpen(MMHANDLE, 0, ip_addr)) != 0) {
		fprintf(stderr, "(%s, %d): init_sensoray: BoardOpen() fault: %d.\n", __FILE__, __LINE__, faults);
		return NULL;

	}
	// Reset io system
	S26_ResetNetwork(MMHANDLE);
	// Detect and register modules connected to the mm
	if ((faults = S26_RegisterAllIoms(MMHANDLE, MSEC_GATEWAY, &nboards, iom_type, iom_status, GATEWAY_RETRIES)) != 0) {
        fprintf(stderr, "(%s, %d): init_sensoray: S26_RegisterAllIoms failed.\n", __FILE__, __LINE__);
        fprintf(stderr, "Found %d boards though.\n", nboards);
        return NULL;
    }
	// Create transaction
	HX xaction;
	if ((xaction = create_xaction()) == 0) {
        fprintf(stderr, "(%s, %d): init_sensoray: Could not create transaction.\n", __FILE__, __LINE__);
		return NULL;
	}
	// Disable watchdog.
	S26_Sched2601_SetWatchdog(xaction, 0);
	if (exec_xaction(xaction)) {
		fprintf(stderr, "(%s, %d): init_sensoray: Transaction failed.\n", __FILE__, __LINE__);
		return NULL;
	}

	// Now look through iom_type and find 2608's...
	PyObject *ret = PyList_New(0);
	if (ret == NULL) {
		Py_XDECREF(ret); // probably unnecessary
		fprintf(stderr, "(%s, %d): init_sensoray: PyList_New failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	for (long i=0; i<16; i++) {
		if (iom_type[i] == 2608) { // NOT SURE ABOUT THIS YET!!!!
			if (PyList_Append(ret, PyLong_FromLong(i)) == -1) {
				Py_XDECREF(ret);
				fprintf(stderr, "(%s, %d): init_sensoray: PyList_Append failed.\n", __FILE__, __LINE__);
				return NULL;
			}
		}
	}
	return ret;
}

static PyObject *reset_iom(PyObject *self, PyObject *args) {
	int iomport;
	u32 faults;
	if (!PyArg_ParseTuple(args, "i", &iomport)) {
		fprintf(stderr, "(%s, %d): reset_iom: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	if ((faults = S26_ResetIom(MMHANDLE, (IOMPORT)iomport, MSEC_GATEWAY, GATEWAY_RETRIES)) != 0) {
		fprintf(stderr, "(%s, %d): reset_iom: ResetIom() failed. fault: %d.\n", __FILE__, __LINE__, faults);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *get_2608_caldata(PyObject *self, PyObject *args) {
	// Benchmark: 3.3 ms
	int iomport;
	if (!PyArg_ParseTuple(args, "i", &iomport)) {
		fprintf(stderr, "(%s, %d): get_2608_caldata: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	HX xaction = create_xaction();
	S26_Sched2608_GetCalData(xaction, (IOMPORT)iomport, 0);
	if (exec_xaction(xaction)) {
		fprintf(stderr, "(%s, %d): get_2608_caldata: Transaction failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *get_2608_aout(PyObject *self, PyObject *args) {
	// Benchmark: 0.9 ms
	int iomport, chan;
	double volts;
	if (!PyArg_ParseTuple(args, "ii", &iomport, &chan)) {
		fprintf(stderr, "(%s, %d): get_2608_aout: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	HX xaction = create_xaction();
	S26_Sched2608_GetAout(xaction, (IOMPORT)iomport, (u8)chan, &volts);
	if (exec_xaction(xaction)) {
		fprintf(stderr, "(%s, %d): get_2608_aout: Transaction failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	return PyFloat_FromDouble(volts);
}

static PyObject *set_2608_aout(PyObject *self, PyObject *args) {
	// Benchmark: 0.9 ms
	int iomport, chan;
	double volts;
	if (!PyArg_ParseTuple(args, "iid", &iomport, &chan, &volts)) {
		fprintf(stderr, "(%s, %d): set_2608_aout: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	HX xaction = create_xaction();
	S26_Sched2608_SetAout(xaction, (IOMPORT)iomport, (u8)chan, volts);
	if (exec_xaction(xaction)) {
		fprintf(stderr, "(%s, %d): set_2608_aout: Transaction failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *get_2608_ains(PyObject *self, PyObject *args) {
	// Benchmark: 4.1 ms
	int iomport;
	double ains[16];
	const u8 ain_types[] = {
		V_10_TYPE,	// chan 0: 10V range on channels 0-15.
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 2
		V_10_TYPE, 	// chan 3
		V_10_TYPE,	// chan 4
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 6
		V_10_TYPE, 	// chan 7
		V_10_TYPE,	// chan 8
		V_10_TYPE,	// chan 9
		V_10_TYPE,	// chan 10
		V_10_TYPE,	// chan 11
		V_10_TYPE,	// chan 12
		V_10_TYPE,	// chan 13
		V_10_TYPE,	// chan 14
		V_10_TYPE	// chan 15
	};
	if (!PyArg_ParseTuple(args, "i", &iomport)) {
		fprintf(stderr, "(%s, %d): get_2608_ains: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	HX xaction = create_xaction();
	S26_Sched2608_SetAinTypes(xaction, (IOMPORT)iomport, ain_types );
	S26_Sched2608_GetAins(xaction, (IOMPORT)iomport, ains, 0); // 0 for "snapshot". 1 for integrated.
	if (exec_xaction(xaction)) {
		fprintf(stderr, "(%s, %d): get_2608_ains: Transaction failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	PyObject *ret = PyList_New(16);
	if (ret == NULL) {
		Py_XDECREF(ret); // probably unnecessary
		fprintf(stderr, "(%s, %d): get_2608_ains: PyList_New failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	for (int i=0; i<16; i++) {
		if (PyList_SetItem(ret, i, PyFloat_FromDouble(ains[i])) == -1) {
			Py_XDECREF(ret);
			fprintf(stderr, "(%s, %d): get_2608_ains: PyList_SetItem failed.\n", __FILE__, __LINE__);
			return NULL;
		}
	}
	return ret;
}

static PyObject *get_2608_ain(PyObject *self, PyObject *args) {
	// Benchmark: 4.1 ms
	int iomport, chan;
	double ains[16];
	const u8 ain_types[] = {
		V_10_TYPE,	// chan 0: 10V range on channels 0-15.
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 2
		V_10_TYPE, 	// chan 3
		V_10_TYPE,	// chan 4
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 6
		V_10_TYPE, 	// chan 7
		V_10_TYPE,	// chan 8
		V_10_TYPE,	// chan 9
		V_10_TYPE,	// chan 10
		V_10_TYPE,	// chan 11
		V_10_TYPE,	// chan 12
		V_10_TYPE,	// chan 13
		V_10_TYPE,	// chan 14
		V_10_TYPE	// chan 15
	};
	if (!PyArg_ParseTuple(args, "ii", &iomport, &chan)) {
		fprintf(stderr, "(%s, %d): get_2608_ains: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	HX xaction = create_xaction();
	S26_Sched2608_SetAinTypes(xaction, (IOMPORT)iomport, ain_types );
	S26_Sched2608_GetAins(xaction, (IOMPORT)iomport, ains, 0); // 0 for "snapshot". 1 for integrated.
	if (exec_xaction(xaction)) {
		fprintf(stderr, "(%s, %d): get_2608_ains: Transaction failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	return  PyFloat_FromDouble(ains[chan]);
}

static PyObject *get_2608_4ains_magnet(PyObject *self, PyObject *args) {
	// Benchmark: 4.1 ms
	int iomport, chan1, chan2, chan3, chan4;
	double ains[16];
	const u8 ain_types[] = {
		V_10_TYPE,	// chan 0: 10V range on channels 0-15.
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 2
		V_10_TYPE, 	// chan 3
		V_10_TYPE,	// chan 4
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 6
		V_10_TYPE, 	// chan 7
		V_10_TYPE,	// chan 8
		V_10_TYPE,	// chan 9
		V_10_TYPE,	// chan 10
		V_10_TYPE,	// chan 11
		V_10_TYPE,	// chan 12
		V_10_TYPE,	// chan 13
		V_10_TYPE,	// chan 14
		V_10_TYPE	// chan 15
	};
	if (!PyArg_ParseTuple(args, "iiiii", &iomport, &chan1, &chan2, &chan3, &chan4)) {
		fprintf(stderr, "(%s, %d): get_2608_ains: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	HX xaction = create_xaction();
	S26_Sched2608_SetAinTypes(xaction, (IOMPORT)iomport, ain_types );
	S26_Sched2608_GetAins(xaction, (IOMPORT)iomport, ains, 0); // 0 for "snapshot". 1 for integrated.
	if (exec_xaction(xaction)) {
		fprintf(stderr, "(%s, %d): get_2608_ains: Transaction failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	PyObject *ret = PyList_New(4);
	PyList_SetItem(ret, 0, PyFloat_FromDouble(ains[chan1]));
	PyList_SetItem(ret, 1, PyFloat_FromDouble(ains[chan2]));
	PyList_SetItem(ret, 2, PyFloat_FromDouble(ains[chan3]));
	PyList_SetItem(ret, 3, PyFloat_FromDouble(ains[chan4]));
	return ret;
}

static PyObject *get_2608_5ains_magnet(PyObject *self, PyObject *args) {
	// Benchmark: 4.1 ms
	int iomport, chan1, chan2, chan3, chan4, chan5;
	double ains[16];
	const u8 ain_types[] = {
		V_10_TYPE,	// chan 0: 10V range on channels 0-15.
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 2
		V_10_TYPE, 	// chan 3
		V_10_TYPE,	// chan 4
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 6
		V_10_TYPE, 	// chan 7
		V_10_TYPE,	// chan 8
		V_10_TYPE,	// chan 9
		V_10_TYPE,	// chan 10
		V_10_TYPE,	// chan 11
		V_10_TYPE,	// chan 12
		V_10_TYPE,	// chan 13
		V_10_TYPE,	// chan 14
		V_10_TYPE	// chan 15
	};
	if (!PyArg_ParseTuple(args, "iiiiii", &iomport, &chan1, &chan2, &chan3, &chan4, &chan5)) {
		fprintf(stderr, "(%s, %d): get_2608_ains: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	HX xaction = create_xaction();
	S26_Sched2608_SetAinTypes(xaction, (IOMPORT)iomport, ain_types );
	S26_Sched2608_GetAins(xaction, (IOMPORT)iomport, ains, 0); // 0 for "snapshot". 1 for integrated.
	if (exec_xaction(xaction)) {
		fprintf(stderr, "(%s, %d): get_2608_ains: Transaction failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	PyObject *ret = PyList_New(5);
	PyList_SetItem(ret, 0, PyFloat_FromDouble(ains[chan1]));
	PyList_SetItem(ret, 1, PyFloat_FromDouble(ains[chan2]));
	PyList_SetItem(ret, 2, PyFloat_FromDouble(ains[chan3]));
	PyList_SetItem(ret, 3, PyFloat_FromDouble(ains[chan4]));
	PyList_SetItem(ret, 4, PyFloat_FromDouble(ains[chan5]));
	return ret;
}

static PyObject *get_2608_2ains_magnet(PyObject *self, PyObject *args) {
	// Benchmark: 4.1 ms
	int iomport, chan1, chan2;
	double ains[16];
	const u8 ain_types[] = {
		V_10_TYPE,	// chan 0: 10V range on channels 0-15.
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 2
		V_10_TYPE, 	// chan 3
		V_10_TYPE,	// chan 4
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 6
		V_10_TYPE, 	// chan 7
		V_10_TYPE,	// chan 8
		V_10_TYPE,	// chan 9
		V_10_TYPE,	// chan 10
		V_10_TYPE,	// chan 11
		V_10_TYPE,	// chan 12
		V_10_TYPE,	// chan 13
		V_10_TYPE,	// chan 14
		V_10_TYPE	// chan 15
	};
	if (!PyArg_ParseTuple(args, "iii", &iomport, &chan1, &chan2)) {
		fprintf(stderr, "(%s, %d): get_2608_ains: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	HX xaction = create_xaction();
	S26_Sched2608_SetAinTypes(xaction, (IOMPORT)iomport, ain_types );
	S26_Sched2608_GetAins(xaction, (IOMPORT)iomport, ains, 0); // 0 for "snapshot". 1 for integrated.
	if (exec_xaction(xaction)) {
		fprintf(stderr, "(%s, %d): get_2608_ains: Transaction failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	PyObject *ret = PyList_New(2);
	PyList_SetItem(ret, 0, PyFloat_FromDouble(ains[chan1]));
	PyList_SetItem(ret, 1, PyFloat_FromDouble(ains[chan2]));
	return ret;
}

static PyObject *get_multiple_2608_ains(PyObject *self, PyObject *args) {
	PyObject *iomports;
	if (!PyArg_ParseTuple(args, "O", &iomports)) {
		fprintf(stderr, "(%s, %d): get_multiple_2608_ains: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	if (!PyList_Check(iomports)) {
		fprintf(stderr, "(%s, %d): get_multiple_2608_ains: You must provide a list of iomports.\n", __FILE__, __LINE__);
		return NULL;
	}
	int n;
	if ((n = PyList_Size(iomports)) < 1) {
		fprintf(stderr, "(%s, %d): get_multiple_2608_ains: You must provide a list of iomports.\n", __FILE__, __LINE__);
		return NULL;
	}
	double all_ains[16*n];
	const u8 ain_types[] = {
		V_10_TYPE,	// chan 0: 10V range on channels 0-15.
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 2
		V_10_TYPE, 	// chan 3
		V_10_TYPE,	// chan 4
		V_10_TYPE,	// chan 1
		V_10_TYPE,	// chan 6
		V_10_TYPE, 	// chan 7
		V_10_TYPE,	// chan 8
		V_10_TYPE,	// chan 9
		V_10_TYPE,	// chan 10
		V_10_TYPE,	// chan 11
		V_10_TYPE,	// chan 12
		V_10_TYPE,	// chan 13
		V_10_TYPE,	// chan 14
		V_10_TYPE	// chan 15
	};
	HX xaction = create_xaction();
	for (int i=0; i<n; i++) {
		IOMPORT iomport = PyLong_AsLong(PyList_GetItem(iomports, i));
		S26_Sched2608_SetAinTypes(xaction, iomport, ain_types);
		S26_Sched2608_GetAins(xaction, iomport, all_ains+16*i, 1); // 0 for "snapshot". 1 for integrated.
	}
	if (exec_xaction(xaction)) {
		fprintf(stderr, "(%s, %d): get_multiple_2608_ains: Transaction failed.\n", __FILE__, __LINE__);
		return NULL;
	}

	PyObject *ret = PyDict_New();
	if (ret == NULL) {
		Py_XDECREF(ret); // probably unnecessary
		fprintf(stderr, "(%s, %d): get_multiple_2608_ains: PyDict_New failed.\n", __FILE__, __LINE__);
		return NULL;
	}
	for (int i=0; i<n; i++) {
		double *ains = all_ains+16*i;
		PyObject *list = PyList_New(16);
		if (list == NULL) {
			Py_XDECREF(list); // probably unnecessary
			Py_XDECREF(ret);
			fprintf(stderr, "(%s, %d): get_multiple_2608_ains: PyList_New failed.\n", __FILE__, __LINE__);
			return NULL;
		}
		for (int j=0; j<16; j++) {
			if (PyList_SetItem(list, j, PyFloat_FromDouble(ains[j])) == -1) {
				Py_XDECREF(list);
				Py_XDECREF(ret);
				fprintf(stderr, "(%s, %d): get_multiple_2608_ains: PyList_SetItem failed.\n", __FILE__, __LINE__);
				return NULL;
			}
		}
		if (PyDict_SetItem(ret, PyList_GetItem(iomports, i), list) == -1) {
			Py_XDECREF(list);
			Py_XDECREF(ret);
			fprintf(stderr, "(%s, %d): get_multiple_2608_ains: PyDict_SetItem failed.\n", __FILE__, __LINE__);
			return NULL;
		}
	}
	return ret;
}

static PyObject *init_2608_ain_files(PyObject *self, PyObject *args) {
	AinFiles *ain_files = (AinFiles *)malloc(sizeof(AinFiles));
	int iomport;
	double bad_val = DBL_MIN;
	if (!PyArg_ParseTuple(args, "i|d", &iomport, &bad_val)) {
		fprintf(stderr, "(%s, %d): init_2608_ain_files: could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	if (ain_files == NULL) {
		fprintf(stderr, "(%s, %d): init_2608_ain_files: could not allocate AinFiles struct.\n", __FILE__, __LINE__);
		return NULL;
	}
	ain_files->iomport = (IOMPORT)iomport;
	ain_files->bad_val = bad_val;
	for (int i=0; i<16; i++) {
		ain_files->f[i] = NULL;
	}
	return PyCapsule_New((void *)ain_files, NULL, free_ain_files);
}

static PyObject *open_2608_ain_file(PyObject *self, PyObject *args) {
	PyObject *ain_files_cobject;
	char *fname;
	int channel;
	if (!PyArg_ParseTuple(args, "Osi", &ain_files_cobject, &fname, &channel)) {
		fprintf(stderr, "(%s, %d): open_2608_ain_file: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	if (channel < 0 || 16 <= channel) {
		fprintf(stderr, "(%s, %d): open_2608_ain_file: channel out of range.\n", __FILE__, __LINE__);
		return NULL;
	}
	AinFiles *ain_files = (AinFiles *)PyCapsule_GetPointer(ain_files_cobject,NULL);
	ain_files->f[channel] = fopen(fname, "w");
	if (ain_files->f[channel] == NULL) {
		fprintf(stderr, "(%s, %d): open_2608_ain_file: Failed to open file.\n", __FILE__, __LINE__);
		return NULL;
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *write_2608_ains(PyObject *self, PyObject *args) {
	PyObject *ain_files_cobject;
	if (!PyArg_ParseTuple(args, "O", &ain_files_cobject)) {
		fprintf(stderr, "(%s, %d): write_2608_ains: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	AinFiles *ain_files = (AinFiles *)PyCapsule_GetPointer(ain_files_cobject,NULL);

	double ains[16];
	HX xaction = create_xaction();
	S26_Sched2608_GetAins(xaction, ain_files->iomport, ains, 0); // 0 for "snapshot". 1 for integrated.
	if (exec_xaction(xaction)) {
		// Write bad value
		double *bad_val = &(ain_files->bad_val);
		for (int i=0; i<16; i++) {
			if (ain_files->f[i] != NULL) {
				fwrite((void *)bad_val, sizeof(double), 1, ain_files->f[i]);
			}
		}
		//fprintf(stderr, "(%s, %d): write_2608_ains: Transaction failed.\n", __FILE__, __LINE__);
		//return NULL;
	}
	else {
		for (int i=0; i<16; i++) {
			if (ain_files->f[i] != NULL) {
				fwrite((void *)(ains+i), sizeof(double), 1, ain_files->f[i]);
			}
		}
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *flush_2608_ain_files(PyObject *self, PyObject *args) {
	PyObject *ain_files_cobject;
	if (!PyArg_ParseTuple(args, "O", &ain_files_cobject)) {
		fprintf(stderr, "(%s, %d): flush_2608_ain_files: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	AinFiles *ain_files = (AinFiles *)PyCapsule_GetPointer(ain_files_cobject,NULL);
	for (int i=0; i<16; i++) {
		fflush(ain_files->f[i]);
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static PyObject *write_multiple_2608_ains(PyObject *self, PyObject *args) {
	PyObject *ain_files_cobject_list;
	if (!PyArg_ParseTuple(args, "O", &ain_files_cobject_list)) {
		fprintf(stderr, "(%s, %d): write_multiple_2608_ains: Could not parse args.\n", __FILE__, __LINE__);
		return NULL;
	}
	if (!PyList_Check(ain_files_cobject_list)) {
		fprintf(stderr, "(%s, %d): write_multiple_2608_ains: You must provide a list of ain_files cobjects.\n", __FILE__, __LINE__);
		return NULL;
	}
	int n;
	if ((n = PyList_Size(ain_files_cobject_list)) < 1) {
		fprintf(stderr, "(%s, %d): write_multiple_2608_ains: You must provide a list of ain_files cobjects.\n", __FILE__, __LINE__);
		return NULL;
	}
	double all_ains[16*n];
	AinFiles *ain_files[n];
	HX xaction = create_xaction();
	for (int i=0; i<n; i++) {
		ain_files[i] = (AinFiles *)PyCapsule_GetPointer(PyList_GetItem(ain_files_cobject_list, i),NULL);
		S26_Sched2608_GetAins(xaction, ain_files[i]->iomport, all_ains+16*i, 0); // 0 for "snapshot". 1 for integrated.
	}
	if (exec_xaction(xaction)) {
		// Write bad value
		double *bad_val = &(ain_files[0]->bad_val);
		for (int i=0; i<n; i++) {
			for (int j=0; j<16; j++) {
				if (ain_files[i]->f[j] != NULL) {
					fwrite((void *)bad_val, sizeof(double), 1, ain_files[i]->f[j]);
				}
			}
		}
		//fprintf(stderr, "(%s, %d): write_multiple_2608_ains: Transaction failed.\n", __FILE__, __LINE__);
		//return NULL;
	}
	else {
		for (int i=0; i<n; i++) {
			for (int j=0; j<16; j++) {
				if (ain_files[i]->f[j] != NULL) {
					fwrite((void *)(all_ains+i*16+j), sizeof(double), 1, ain_files[i]->f[j]);
				}
			}
		}
	}
	Py_INCREF(Py_None);
	return Py_None;
}

static inline HX create_xaction() {
	return S26_SchedOpen(MMHANDLE, GATEWAY_RETRIES);
}

static u32 exec_xaction(HX x) {
	u8 iom_status[16];
	u32 err = S26_SchedExecute(x, MSEC_GATEWAY, iom_status);
	if (err != 0) {
		print_error_info(err, iom_status);
	}
	return err;
}

static void print_error_info(u32 gwerr, u8 *iom_status) {
	char errmsg[128];
	int extra_info = gwerr & ~GWERRMASK;
	u8 status = iom_status[extra_info];
	switch (gwerr & GWERRMASK) {
        case GWERR_IOMSPECIFIC:
            fprintf(stderr, "Iom-specific error on iomport %d\n", extra_info);
            break;
        case GWERR_BADVALUE:
            fprintf(stderr, "Illegal value for argument %d\n", extra_info);
            break;
        case GWERR_IOMCLOSED:
            fprintf(stderr, "Iom is not open\n");
            break;
        case GWERR_IOMERROR:
            fprintf(stderr, "Iom CERR asserted\n");
            break;
        case GWERR_IOMNORESPOND:
            fprintf(stderr, "Bad module response from iomport %d\n", extra_info);
            break;
        case GWERR_IOMRESET:
            fprintf(stderr, "Module RST asserted\n");
            if (status) {
                fprintf(stderr, "    GWERR_IOMRESET encountered. Module reset necessary.\n"); //. Iom type: %i\n", iom_type[extra_info]);
                // If this happens, we need to reset the module!!!!
            }
            break;
        case GWERR_IOMTYPE:
            fprintf(stderr, "Action not supported by iom type.\n");
            break;
        case GWERR_MMCLOSED:
            fprintf(stderr, "MM is closed.\n");
            break;
        case GWERR_MMNORESPOND:
            fprintf(stderr, "MM response timed out.\n");
            break;
        case GWERR_PACKETSEND:
            fprintf(stderr, "Failed to send cmd packet.\n");
            break;
        case GWERR_TOOLARGE:
            fprintf(stderr, "Command or response packet too large.\n");
            break;
        case GWERR_XACTALLOC:
            fprintf(stderr, "Transaction object allocation problem.\n");
            break;
        default:
            fprintf(stderr, "Unknown error.\n");
            break;
    }
    if ((gwerr & GWERRMASK) != GWERR_IOMRESET) {
        fprintf(stderr, "Error (non-fatal): 0x%X (%s).\n", (int)gwerr, errmsg);
	}
}

static void free_ain_files(PyObject *capsule) {
	AinFiles *ain_files = (AinFiles *)PyCapsule_GetPointer(capsule, NULL);
	for (int i=0; i<16; i++) {
		if (ain_files->f[i] != NULL) {
			fclose(ain_files->f[i]);
		}
	}
	free(ain_files);
}
