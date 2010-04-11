/*
 * General include file for MMTK C modules.
 *
 * Written by Konrad Hinsen
 * last revision: 2007-1-11 */

#ifndef MMTK_H

#include "Python.h"

#include "MMTK/arrayobject.h"

/* Provide Py_ssize_t for Python < 2.5 */
#if PY_VERSION_HEX < 0x02050000
#if !defined(PY_SSIZE_T_COMPATIBILITY)
#define PY_SSIZE_T_COMPATIBILITY
#if !defined(NUMPY)
typedef int Py_ssize_t;
#endif
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#define PyInt_FromSsize_t(n) PyInt_FromLong(n)
typedef Py_ssize_t (*lenfunc)(PyObject *);
typedef PyObject *(*ssizeargfunc)(PyObject *, Py_ssize_t);
typedef PyObject *(*ssizessizeargfunc)(PyObject *, Py_ssize_t, Py_ssize_t);
typedef int(*ssizeobjargproc)(PyObject *, Py_ssize_t, PyObject *);
typedef int(*ssizessizeobjargproc)(PyObject *, Py_ssize_t, Py_ssize_t, PyObject *);
typedef Py_ssize_t (*readbufferproc)(PyObject *, Py_ssize_t, void **);
typedef Py_ssize_t (*writebufferproc)(PyObject *, Py_ssize_t, void **);
typedef Py_ssize_t (*segcountproc)(PyObject *, Py_ssize_t *);
typedef Py_ssize_t (*charbufferproc)(PyObject *, Py_ssize_t, char **);
#endif
#endif

/* MinGW doesn't have this */
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Configuration parameters */

/* max. number of threads that can try to access the same universe
   in parallel (energy evaluation threads don't count) */
#define MMTK_MAX_THREADS 10

/* Type definitions */

typedef double vector3[3];
typedef double tensor3[3][3];


/* Useful general macros */

#define sqr(x) ((x)*(x))
#define cube(x) ((x)*(x)*(x))
#define vector_add(v1, v2, f) \
   { int i_; for (i_=0; i_<3; i_++) (v1)[i_] += (f)*(v2)[i_]; }
#define vector_length_sq(r) (sqr(r[0])+sqr(r[1])+sqr(r[2]))
#define vector_length(r) (sqrt(vector_length_sq(r)))
#define dot(v1, v2) ((v1)[0]*(v2)[0] + (v1)[1]*(v2)[1] + (v1)[2]*(v2)[2])
#define cross(v, v1, v2) \
        { v[0] = (v1)[1]*(v2)[2]-(v1)[2]*(v2)[1]; \
          v[1] = (v1)[2]*(v2)[0]-(v1)[0]*(v2)[2]; \
          v[2] = (v1)[0]*(v2)[1]-(v1)[1]*(v2)[0];}

#define vector_scale(v, f) { v[0]*=f; v[1]*=f; v[2]*=f; }
#define vector_copy(v1, v2) { (v1)[0]=(v2)[0]; (v1)[1]=(v2)[1]; \
                              (v1)[2]=(v2)[2]; }
#define vector_changesign(v) { v[0]=-v[0]; v[1]=-v[1]; v[2]=-v[2]; }

#define tensor_product(t, v1, v2, f) \
   { int i_,j_; for (i_=0;i_<3;i_++) for (j_=0;j_<3;j_++) \
                (t)[i_][j_]=(f)*(v1)[i_]*(v2)[j_]; }
#define symmetric_tensor_product(t, v1, v2, f) \
   { int i_,j_; for (i_=0;i_<3;i_++) for (j_=0;j_<3;j_++) \
		     t[i_][j_] = f*((v1)[i_]*(v2)[j_]+(v1)[j_]*(v2)[i_]); }
#define tensor_copy(t1, t2) \
   { int i_,j_; for (i_=0;i_<3;i_++) for (j_=0;j_<3;j_++) \
                (t1)[i_][j_] = (t2)[i_][j_]; }
#define tensor_scale(t1, f) \
   { int i_,j_; for (i_=0;i_<3;i_++) for (j_=0;j_<3;j_++) (t1)[i_][j_] *= f; }
#define tensor_add(t1, t2, f) \
   { int i_,j_; for (i_=0;i_<3;i_++) for (j_=0;j_<3;j_++) \
                (t1)[i_][j_] += (f)*t2[i_][j_]; }
#define tensor_changesign(t) { vector_changesign(t[0]); \
                               vector_changesign(t[1]); \
                               vector_changesign(t[2]); }
#define tensor_transpose(t) { double temp_; \
                              temp_=t[0][1]; t[0][1]=t[1][0]; t[1][0]=temp_; \
			      temp_=t[0][2]; t[0][2]=t[2][0]; t[2][0]=temp_; \
			      temp_=t[1][2]; t[1][2]=t[2][1]; t[2][1]=temp_; }


/* Constants */

/* Numbers larger than 'undefined_limit' are considered to be undefined in
 * certain situations. This is used e.g. to represent unknown positions.
 * The value 'undefined' is used to mark numbers as undefined. The difference
 * between these two values should make sure that undefined values are
 * recognized across floating point representation boundaries.
 */
#define undefined_limit 1.e30;
#define undefined 1.e31;


#define MMTK_H
#endif
