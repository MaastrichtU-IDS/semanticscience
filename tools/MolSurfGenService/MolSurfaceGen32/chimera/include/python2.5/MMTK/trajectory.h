/*
 * Include file for trajectory objects
 *
 * Written by Konrad Hinsen
 * last revision: 2007-11-27
 */

#ifndef MMTK_TRAJECTORY_H

/* General include files */

#include "MMTK/core.h"
#include "Scientific/netcdfmodule.h"
#ifdef USE_NETCDF_H_FROM_SCIENTIFIC
# include "Scientific/netcdf.h"
#else
# include "netcdf.h"
#endif
#include <time.h>

/* Unit names */

#define length_unit_name "nanometer"
#define volume_unit_name "nanometer3"
#define time_unit_name "picosecond"
#define frequency_unit_name "picosecond-1"
#define frequency_square_unit_name "picosecond-2"
#define velocity_unit_name "nanometer picosecond-1"
#define mass_unit_name "atomic_mass_unit"
#define energy_unit_name "kilojoule mole-1"
#define energy_gradient_unit_name "kilojoule mole-1 nanometer-1"
#define temperature_unit_name "kelvin"
#define pressure_unit_name "kilojoule mole-1 nanometer-3"

/* Trajectory object structure */

typedef struct {
  PyObject_HEAD
  PyObject *universe;
  PyArrayObject *index_map;
  PyNetCDFFileObject *file;
  PyNetCDFVariableObject *var_step;
  PyArrayObject *sbuffer, *vbuffer;
  PyArrayObject *box_buffer;
  clock_t last_flush;
  int box_buffer_first, box_buffer_last, box_buffer_skip;
  int floattype;
  int natoms, trajectory_atoms;
  int steps;
  int block_size;
  int cycle;
  int first_step;
  int write;
} PyTrajectoryObject;

extern PyTypeObject PyTrajectory_Type;


/* Trajectory variable types */

enum PyTrajectory_VariableTypes { PyTrajectory_Scalar,
				  PyTrajectory_ParticleScalar,
				  PyTrajectory_ParticleVector,
                                  PyTrajectory_IntScalar,
                                  PyTrajectory_BoxSize };

enum PyTrajectory_DataClass { PyTrajectory_Configuration = 1,
			      PyTrajectory_Velocities = 2,
			      PyTrajectory_Gradients = 4,
			      PyTrajectory_Energy = 8,
			      PyTrajectory_Thermodynamic = 16,
			      PyTrajectory_Time = 32,
                              PyTrajectory_Internal = 64,
			      PyTrajectory_Auxiliary = 128 };

typedef struct {
  char *name;
  char *text;
  char *unit;
  union data { int *ip; double *dp; PyArrayObject *array; } value;
  int length;
  int type;
  int class;
  int modified;
} PyTrajectoryVariable;

/* Trajectory function declaration */

typedef int trajectory_fn(PyTrajectoryVariable *, PyObject *,
			  int step, void **scratch);

/* Output specification structure */

typedef struct {
  PyObject *destination;
  PyObject **variables;
  trajectory_fn *function;
  PyObject *parameters;
  void *scratch;
  int first;
  int last;
  int frequency;
  int type;
  int close;
  int what;
} PyTrajectoryOutputSpec;


/*
 * C API functions
 */

/* Type definitions */
#define PyTrajectory_Type_NUM 0

/* Open a trajectory file */
#define PyTrajectory_Open_RET PyTrajectoryObject *
#define PyTrajectory_Open_PROTO Py_PROTO((PyObject *universe, \
					  PyObject *description, \
					  PyArrayObject *index_map, \
					  char *filename, char *mode, \
                                          int floatttype, int cycle, \
                                          int block_size))
#define PyTrajectory_Open_NUM 1

/* Close a trajectory file */
#define PyTrajectory_Close_RET int
#define PyTrajectory_Close_PROTO Py_PROTO((PyTrajectoryObject *trajectory))
#define PyTrajectory_Close_NUM 2

/* Prepare output */
#define PyTrajectory_OutputSpecification_RET PyTrajectoryOutputSpec *
#define PyTrajectory_OutputSpecification_PROTO \
     Py_PROTO((PyObject *universe, PyListObject *spec_list, char *description,\
	       PyTrajectoryVariable *data))
#define PyTrajectory_OutputSpecification_NUM 3

/* Finish output */
#define PyTrajectory_OutputFinish_RET void
#define PyTrajectory_OutputFinish_PROTO \
     Py_PROTO((PyTrajectoryOutputSpec *spec, int step, int error_flag,\
	       int time_stamp_flag, PyTrajectoryVariable *data))
#define PyTrajectory_OutputFinish_NUM 4

/* Do output */
#define PyTrajectory_Output_RET int
#define PyTrajectory_Output_PROTO \
     Py_PROTO((PyTrajectoryOutputSpec *spec, int step, \
	       PyTrajectoryVariable *data, PyThreadState **thread))
#define PyTrajectory_Output_NUM 5

/* Total number of C API pointers */
#define PyTrajectory_API_pointers 6


#ifdef _TRAJECTORY_MODULE

/* Type object declarations */
extern PyTypeObject PyTrajectory_Type;

/* Type check macros */
#define PyTrajectory_Check(op) ((op)->ob_type == &PyTrajectory_Type)

/* C API function declarations */
static PyTrajectory_Open_RET PyTrajectory_Open PyTrajectory_Open_PROTO;
static PyTrajectory_Close_RET PyTrajectory_Close PyTrajectory_Close_PROTO;
static PyTrajectory_OutputSpecification_RET PyTrajectory_OutputSpecification \
       PyTrajectory_OutputSpecification_PROTO;
static PyTrajectory_OutputFinish_RET PyTrajectory_OutputFinish \
       PyTrajectory_OutputFinish_PROTO;
static PyTrajectory_Output_RET PyTrajectory_Output \
       PyTrajectory_Output_PROTO;

#else

/* C API address pointer */ 
static void **PyTrajectory_API;

/* Type check macros */
#define PyTrajectory_Check(op) \
   ((op)->ob_type == (PyTypeObject *)PyTrajectory_API[PyTrajectory_Type_NUM])

/* C API function declarations */
#define PyTrajectory_Open \
  (*(PyTrajectory_Open_RET (*)PyTrajectory_Open_PROTO) \
   PyTrajectory_API[PyTrajectory_Open_NUM])
#define PyTrajectory_Close \
  (*(PyTrajectory_Close_RET (*)PyTrajectory_Close_PROTO) \
   PyTrajectory_API[PyTrajectory_Close_NUM])
#define PyTrajectory_OutputSpecification \
  (*(PyTrajectory_OutputSpecification_RET \
     (*)PyTrajectory_OutputSpecification_PROTO) \
   PyTrajectory_API[PyTrajectory_OutputSpecification_NUM])
#define PyTrajectory_OutputFinish \
  (*(PyTrajectory_OutputFinish_RET \
     (*)PyTrajectory_OutputFinish_PROTO) \
   PyTrajectory_API[PyTrajectory_OutputFinish_NUM])
#define PyTrajectory_Output \
  (*(PyTrajectory_Output_RET \
     (*)PyTrajectory_Output_PROTO) \
   PyTrajectory_API[PyTrajectory_Output_NUM])

#endif

/* Import macro */
#define import_MMTK_trajectory() \
{ \
  PyObject *module = PyImport_ImportModule("MMTK_trajectory"); \
  if (module != NULL) { \
    PyObject *module_dict = PyModule_GetDict(module); \
    PyObject *c_api_object = PyDict_GetItemString(module_dict, "_C_API"); \
    if (PyCObject_Check(c_api_object)) { \
      PyTrajectory_API = (void **)PyCObject_AsVoidPtr(c_api_object); \
    } \
  } \
}

#define MMTK_TRAJECTORY_H
#endif
