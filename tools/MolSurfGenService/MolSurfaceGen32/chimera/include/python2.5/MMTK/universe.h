/* Include file for C universe-related functions.
 *
 * Written by Konrad Hinsen
 * last revision: 2007-4-23
 */

#ifndef MMTK_UNIVERSE_H

#include "MMTK/core.h"

#ifdef WITH_THREAD
#include "pythread.h"
#endif

/* Type definitions */

typedef void distance_fn(vector3 d, vector3 r1, vector3 r2, double *data);
typedef void correction_fn(vector3 *x, int natoms, double *data);
typedef double volume_fn(double scale_factor, double *data);
typedef void box_fn(vector3 *x, vector3 *b, int n, double *data, int to_box);
typedef void bounding_box_fn(vector3 *box1, vector3 *box2, vector3 *x,
			     int n, double *data);


/* Universe specification object structure */

typedef struct {
  PyObject_HEAD
  PyArrayObject *geometry;
  double *geometry_data;
  distance_fn *distance_function;
  correction_fn *correction_function;
  volume_fn *volume_function;
  box_fn *box_function;
  box_fn *trajectory_function;
  bounding_box_fn *bounding_box_function;
#ifdef WITH_THREAD
  PyThread_type_lock configuration_change_lock;
  PyThread_type_lock main_state_lock;
  PyThread_type_lock state_wait_lock[MMTK_MAX_THREADS];
  int state_access_type[MMTK_MAX_THREADS];
  int state_access;
  int waiting_threads;
#endif
  int is_periodic;
  int is_orthogonal;
  int geometry_data_length;
} PyUniverseSpecObject;


/* Macro definitions */

/* Distance vector in infinite universe */
#define distance_vector_1(d, r1, r2, data) \
  { \
    d[0] = r2[0]-r1[0]; \
    d[1] = r2[1]-r1[1]; \
    d[2] = r2[2]-r1[2]; \
  }

/* Distance vector in orthorhombic universe */
#define distance_vector_2(d, r1, r2, data) \
  { \
    double xh = 0.5*(data)[0]; \
    double yh = 0.5*(data)[1]; \
    double zh = 0.5*(data)[2]; \
    d[0] = r2[0]-r1[0]; \
    if (d[0] > xh) d[0] -= (data)[0]; \
    if (d[0] <= -xh) d[0] += (data)[0]; \
    d[1] = r2[1]-r1[1]; \
    if (d[1] > yh) d[1] -= (data)[1]; \
    if (d[1] <= -yh) d[1] += (data)[1]; \
    d[2] = r2[2]-r1[2]; \
    if (d[2] > zh) d[2] -= (data)[2]; \
    if (d[2] <= -zh) d[2] += (data)[2]; \
  }

/* Distance vector in parallelepipedic universe */
#define distance_vector_3(d, r1, r2, data) \
  { \
    double dx = (r2)[0]-(r1)[0]; \
    double dy = (r2)[1]-(r1)[1]; \
    double dz = (r2)[2]-(r1)[2]; \
    double dfx = (data)[0+9]*dx + (data)[1+9]*dy + (data)[2+9]*dz; \
    double dfy = (data)[3+9]*dx + (data)[4+9]*dy + (data)[5+9]*dz; \
    double dfz = (data)[6+9]*dx + (data)[7+9]*dy + (data)[8+9]*dz; \
    if (dfx > 0.5) dfx -= 1.; \
    if (dfx <= -0.5) dfx += 1.; \
    if (dfy > 0.5) dfy -= 1.; \
    if (dfy <= -0.5) dfy += 1.; \
    if (dfz > 0.5) dfz -= 1.; \
    if (dfz <= -0.5) dfz += 1.; \
    d[0] = (data)[0]*dfx + (data)[1]*dfy + (data)[2]*dfz; \
    d[1] = (data)[3]*dfx + (data)[4]*dfy + (data)[5]*dfz; \
    d[2] = (data)[6]*dfx + (data)[7]*dfy + (data)[8]*dfz; \
  }

/*
 * C API
 */

/* Type definitions */
#define PyUniverseSpec_Type_NUM 0

/* Universe state lock access */
#define PyUniverseSpec_StateLock_RET int
#define PyUniverseSpec_StateLock_PROTO \
        Py_PROTO((PyUniverseSpecObject *universe, int action))
#define PyUniverseSpec_StateLock_NUM 1

/* Total number of C API pointers */
#define PyUniverse_API_pointers 2


#ifdef _UNIVERSE_MODULE

/* Type object declarations */
extern PyTypeObject PyUniverseSpec_Type;

/* Type check macros */
#define PyUniverseSpec_Check(op) ((op)->ob_type == &PyUniverseSpec_Type)

/* C API function declarations */

extern PyUniverseSpec_StateLock_RET PyUniverseSpec_StateLock \
       PyUniverseSpec_StateLock_PROTO;

#else

/* C API address pointer */ 
static void **PyUniverse_API;

/* Type definitions */
#define PyUniverseSpec_Type *(PyTypeObject *) \
                             PyUniverse_API[PyUniverseSpec_Type_NUM]

/* Type check macros */
#define PyUniverseSpec_Check(op) \
   ((op)->ob_type == (PyTypeObject *)PyUniverse_API[PyUniverseSpec_Type_NUM])

/* C API function declarations */
#define PyUniverseSpec_StateLock \
  (*(PyUniverseSpec_StateLock_RET (*)PyUniverseSpec_StateLock_PROTO) \
   PyUniverse_API[PyUniverseSpec_StateLock_NUM])

/* Import macro */
#define import_MMTK_universe() \
{ \
  PyObject *module = PyImport_ImportModule("MMTK_universe"); \
  if (module != NULL) { \
    PyObject *module_dict = PyModule_GetDict(module); \
    PyObject *c_api_object = PyDict_GetItemString(module_dict, "_C_API"); \
    if (PyCObject_Check(c_api_object)) { \
      PyUniverse_API = (void **)PyCObject_AsVoidPtr(c_api_object); \
    } \
  } \
}

#endif

#define MMTK_UNIVERSE_H
#endif
