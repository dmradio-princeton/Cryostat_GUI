#ifndef SENSOPY__H
#define SENSOPY__H

#include "Python.h"
#include "app2600.h"
#include <float.h> // for float limits

#define MMHANDLE       	 0
#define MSEC_GATEWAY   	 100
#define GATEWAY_RETRIES	 50

typedef void *HX;

typedef struct AinFiles {
	IOMPORT iomport;
	FILE *f[16];
	double bad_val;	// what to write when sampling fails.
} AinFiles;

PyMODINIT_FUNC PyInit__sensopy(void);
static PyObject *init_sensoray(PyObject *self, PyObject *args);
static PyObject *reset_iom(PyObject *self, PyObject *args);
static PyObject *get_2608_caldata(PyObject *self, PyObject *args);
static PyObject *get_2608_aout(PyObject *self, PyObject *args);
static PyObject *set_2608_aout(PyObject *self, PyObject *args);
static PyObject *get_2608_ains(PyObject *self, PyObject *args);
static PyObject *get_2608_ain(PyObject *self, PyObject *args);
static PyObject *get_2608_2ains_magnet(PyObject *self, PyObject *args);
static PyObject *get_2608_4ains_magnet(PyObject *self, PyObject *args);
static PyObject *get_2608_5ains_magnet(PyObject *self, PyObject *args);
static PyObject *get_multiple_2608_ains(PyObject *self, PyObject *args);
static PyObject *init_2608_ain_files(PyObject *self, PyObject *args);
static PyObject *open_2608_ain_file(PyObject *self, PyObject *args);
static PyObject *write_2608_ains(PyObject *self, PyObject *args);
static PyObject *flush_2608_ain_files(PyObject *self, PyObject *args);
static PyObject *write_multiple_2608_ains(PyObject *self, PyObject *args);

static inline HX create_xaction(void);
static u32 exec_xaction(HX x);
static void print_error_info(u32 gwerr, u8 *iom_status);
static void free_ain_files(PyObject *capsule);
            
#endif
