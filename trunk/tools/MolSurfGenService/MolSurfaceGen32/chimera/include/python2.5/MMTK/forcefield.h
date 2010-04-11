/* Include file for C force field calculations.
 *
 * Written by Konrad Hinsen
 * last revision: 2006-5-10
 */

#ifndef MMTK_FORCEFIELD_H

/* Common include files */

#include "MMTK/core.h"
#include "MMTK/universe.h"
#include <math.h>

#ifdef WITH_THREAD
#include "pythread.h"
#ifdef HAVE_UNISTD_H
#include <unistd.h>
#endif
#ifdef _POSIX_THREADS
#include <pthread.h>
#endif
#endif

#ifdef WITH_MPI
#include "Scientific/mpimodule.h"
#endif

/* Configurable parameters */

#define MMTK_MAX_TERMS 5  /* Max. energy terms in an energy term object */
#define MMTK_MAX_DATA 40  /* Max. data slots in an energy term object */
/* Global variables */

extern double electrostatic_energy_factor;


/* Type definitions */

typedef struct {
  PyArrayObject *coordinates;
  int natoms;
  int thread_id, proc_id, slice_id, nthreads, nprocs, nslices;
  int small_change;
} energy_spec;

struct ffedata;
struct ffterm;
struct ffeval;

typedef int gradient_function(struct ffedata *energy,
			      int i, vector3 gradient);

typedef int fc_function(struct ffedata *energy,
			int i, int j, tensor3 fc,
			double r_sq);

typedef void ff_eterm_function(struct ffterm *term,
			       struct ffeval *evaluator,
			       energy_spec *input,
			       struct ffedata *energy);

typedef void ff_eval_function(struct ffeval *evaluator,
			      struct ffedata *energy,
			      PyArrayObject *configuration,
			      int small_change);

typedef void energy_retrieval_function(PyObject *, PyObject *);


typedef struct ffedata {
  PyObject *gradients;
  gradient_function *gradient_fn;
  PyObject *force_constants;
  fc_function *fc_fn;
  double *energy_terms;
  double energy;
  double virial;
  int virial_available;
  int error;
} energy_data;

#ifdef WITH_THREAD
typedef struct {
#ifdef _POSIX_THREADS
  pthread_mutex_t lock;
  pthread_cond_t cond;
#else
  PyThread_type_lock lock;
#endif
  int n;
} barrierinfo;

typedef struct {
  struct ffeval *evaluator;
  PyThread_type_lock lock;
  energy_spec input;
  energy_data energy;
  int with_gradients;
  int exit, stop, done;
} threadinfo;
#endif


/* Energy term object structure */

typedef struct ffterm {
  PyObject_HEAD
  PyObject *user_info;
  PyUniverseSpecObject *universe_spec;
  ff_eterm_function *eval_func;
  char *evaluator_name;
  char *term_names[MMTK_MAX_TERMS];
  PyObject *data[MMTK_MAX_DATA];
  void *scratch;
  double param[MMTK_MAX_DATA];
  int index, virial_index, barrier_index;
  int nterms, nbarriers;
  int n;
  int threaded, parallelized, thread_safe;
} PyFFEnergyTermObject;

/* Evaluator object structure */

typedef struct ffeval {
  PyObject_HEAD
  ff_eval_function *eval_func;
  PyArrayObject *terms;
  PyUniverseSpecObject *universe_spec;
  PyArrayObject *energy_terms_array;
  double *energy_terms;
  void *scratch;
#ifdef WITH_THREAD
  PyThreadState *tstate_save;
  PyThread_type_lock global_lock;
  barrierinfo *binfo;
#endif
#ifdef WITH_MPI
  PyMPICommunicatorObject *communicator;
  double *energy_parts;
  double *gradient_parts;
#endif
  int nterms, ntermobjects;
  int nthreads, nprocs, nslices, proc_id;
} PyFFEvaluatorObject;

/* Non-bonded list object structure */

#define NBLIST_NEIGHBORS 5
#define NBLIST_NEIGHBOR_DIMENSION (2*NBLIST_NEIGHBORS+1)

typedef struct {
  int *atoms;
  int ix, iy, iz;
  int n, i;
} nbbox;

enum nblist_iterator_states { nblist_start, nblist_continue, nblist_finished,
                              nblist_start_excluded, nblist_continue_excluded,
                              nblist_start_14, nblist_continue_14 } ;

struct nblist_iterator {
  nbbox *box1, *box2;
  int ibox, jbox, ineighbor, i, j, a1, a2;
  Py_ssize_t n;
  int state;
};

typedef struct {
  PyObject_HEAD 
  struct nblist_iterator iterator;
  PyObject *excluded_pairs;
  PyObject *one_four_pairs;
  PyObject *atom_subset;
  PyUniverseSpecObject *universe_spec;
  vector3 *lastx;
  int *box_number;
  int *box_atoms;
  nbbox *boxes;
  int box_count[3];
  int nboxes;
  int allocated_boxes;
  int neighbors[NBLIST_NEIGHBOR_DIMENSION*NBLIST_NEIGHBOR_DIMENSION
	        *NBLIST_NEIGHBOR_DIMENSION][3];
  int nneighbors;
  double cutoff;
} PyNonbondedListObject;


/* Sparse force constant matrix object */

struct pair_fc {
  tensor3 fc;
  int i, j;
};

struct pair_descr {
  int diffij;
  int index;
};

struct pair_descr_list {
  struct pair_descr *list;
  int nalloc;
  int nused;
};

typedef struct sparse_fc {
  PyObject_HEAD
  struct pair_fc *data;
  struct pair_descr_list *index;
  Py_ssize_t nalloc;
  Py_ssize_t nused;
  int natoms;
  fc_function *fc_fn;
  double cutoff_sq;
} PySparseFCObject; 

/*
 * C API
 */

/* Type definitions */
#define PyFFEnergyTerm_Type_NUM 0
#define PyFFEvaluator_Type_NUM 1
#define PyNonbondedList_Type_NUM 2
#define PySparseFC_Type_NUM 3

/* Create sparce force constant matrix */
#define PySparseFC_New_RET PySparseFCObject *
#define PySparseFC_New_PROTO Py_PROTO((int natoms, int nalloc))
#define PySparseFC_New_NUM 4

/* Zero sparce force constant matrix */
#define PySparseFC_Zero_RET void
#define PySparseFC_Zero_PROTO Py_PROTO((PySparseFCObject *fc))
#define PySparseFC_Zero_NUM 5

/* Find a pair entry in a sparce force constant matrix */
#define PySparseFC_Find_RET double *
#define PySparseFC_Find_PROTO Py_PROTO((PySparseFCObject *fc, int i, int j))
#define PySparseFC_Find_NUM 6

/* Add a pair contribution to a sparce force constant matrix */
#define PySparseFC_AddTerm_RET int
#define PySparseFC_AddTerm_PROTO Py_PROTO((PySparseFCObject *fc, \
					   int i, int j, double *term))
#define PySparseFC_AddTerm_NUM 7

/* Copy data to an array */
#define PySparseFC_CopyToArray_RET void
#define PySparseFC_CopyToArray_PROTO Py_PROTO((PySparseFCObject *fc, \
					       double *data, int lastdim, \
					       int from1, int to1, \
					       int from2, int to2))
#define PySparseFC_CopyToArray_NUM 8

/* Extract data as an array */
#define PySparseFC_AsArray_RET PyObject *
#define PySparseFC_AsArray_PROTO Py_PROTO((PySparseFCObject *fc, \
					   int from1, int to1, \
					   int from2, int to2))
#define PySparseFC_AsArray_NUM 9

/* Multiply with a vector */
#define PySparseFC_VectorMultiply_RET void
#define PySparseFC_VectorMultiply_PROTO Py_PROTO((PySparseFCObject *fc, \
						  double *result, \
						  double *vector, \
						  int from_i, int to_i, \
						  int from_j, int to_j))
#define PySparseFC_VectorMultiply_NUM 10

/* Create energy term */
#define PyFFEnergyTerm_New_RET PyFFEnergyTermObject *
#define PyFFEnergyTerm_New_PROTO Py_PROTO((void))
#define PyFFEnergyTerm_New_NUM 11

/* Create force field evaluator */
#define PyFFEvaluator_New_RET PyFFEvaluatorObject *
#define PyFFEvaluator_New_PROTO Py_PROTO((void))
#define PyFFEvaluator_New_NUM 12

/* Scale by weight vector */
#define PySparseFC_Scale_RET void
#define PySparseFC_Scale_PROTO Py_PROTO((PySparseFCObject *fc, \
					 PyArrayObject *factors))
#define PySparseFC_Scale_NUM 13

/* Update nonbonded list */
#define PyNonbondedListUpdate_RET int
#define PyNonbondedListUpdate_PROTO Py_PROTO((PyNonbondedListObject *nblist, \
                                              int natoms, double *coordinates,\
					      double *geometry_data))
#define PyNonbondedListUpdate_NUM 14

/* Iterate over nonbonded list */
#define PyNonbondedListIterate_RET int
#define PyNonbondedListIterate_PROTO Py_PROTO((PyNonbondedListObject *nblist, \
                                               struct nblist_iterator \
                                                      *iterator))
#define PyNonbondedListIterate_NUM 15

/* Total number of C API pointers */
#define PyFF_API_pointers 16


#ifdef _FORCEFIELD_MODULE

/* Type object declarations */
extern PyTypeObject PyFFEnergyTerm_Type;
extern PyTypeObject PyFFEvaluator_Type;
extern PyTypeObject PyNonbondedList_Type;
extern PyTypeObject PySparseFC_Type;

/* Type check macros */
#define PyFFEnergyTerm_Check(op) ((op)->ob_type == &PyFFEnergyTerm_Type)
#define PyFFEvaluator_Check(op) ((op)->ob_type == &PyFFEvaluator_Type)
#define PyNonbondedList_Check(op) ((op)->ob_type == &PyNonbondedList_Type)
#define PySparseFC_Check(op) ((op)->ob_type == &PySparseFC_Type)

/* C API function declarations */
extern PySparseFC_New_RET PySparseFC_New PySparseFC_New_PROTO;
extern PySparseFC_Zero_RET PySparseFC_Zero PySparseFC_Zero_PROTO;
extern PySparseFC_Find_RET PySparseFC_Find PySparseFC_Find_PROTO;
extern PySparseFC_AddTerm_RET PySparseFC_AddTerm PySparseFC_AddTerm_PROTO;
extern PySparseFC_CopyToArray_RET PySparseFC_CopyToArray \
       PySparseFC_CopyToArray_PROTO;
extern PySparseFC_AsArray_RET PySparseFC_AsArray PySparseFC_AsArray_PROTO;
extern PySparseFC_VectorMultiply_RET PySparseFC_VectorMultiply \
       PySparseFC_VectorMultiply_PROTO;
extern PySparseFC_Scale_RET PySparseFC_Scale PySparseFC_Scale_PROTO;
extern PyFFEnergyTerm_New_RET PyFFEnergyTerm_New PyFFEnergyTerm_New_PROTO;
extern PyFFEvaluator_New_RET PyFFEvaluator_New PyFFEvaluator_New_PROTO;
extern PyNonbondedListUpdate_RET PyNonbondedListUpdate \
       PyNonbondedListUpdate_PROTO;
extern PyNonbondedListIterate_RET PyNonbondedListIterate \
       PyNonbondedListIterate_PROTO;

#else

/* C API address pointer */ 
static void **PyFF_API;

/* Type definitions */
#define PyFFEnergyTerm_Type *(PyTypeObject *)PyFF_API[PyFFEnergyTerm_Type_NUM]
#define PyFFEvaluator_Type *(PyTypeObject *)PyFF_API[PyFFEvaluator_Type_NUM]
#define PyNonbondedList_Type *(PyTypeObject *)PyFF_API[PyNonbondedList_Type_NUM]
#define PySparseFC_Type *(PyTypeObject *)PyFF_API[PySparseFC_Type_NUM]

/* Type check macros */
#define PyFFEnergyTerm_Check(op) \
   ((op)->ob_type == (PyTypeObject *)PyFF_API[PyFFEnergyTerm_Type_NUM])
#define PyFFEvaluator_Check(op) \
   ((op)->ob_type == (PyTypeObject *)PyFF_API[PyFFEvaluator_Type_NUM])
#define PyNonbondedList_Check(op) \
   ((op)->ob_type == (PyTypeObject *)PyFF_API[PyNonbondedList_Type_NUM])
#define PySparseFC_Check(op) \
   ((op)->ob_type == (PyTypeObject *)PyFF_API[PySparseFC_Type_NUM])

/* C API function declarations */
#define PySparseFC_New \
  (*(PySparseFC_New_RET (*)PySparseFC_New_PROTO) \
   PyFF_API[PySparseFC_New_NUM])
#define PySparseFC_Zero \
  (*(PySparseFC_Zero_RET (*)PySparseFC_Zero_PROTO) \
   PyFF_API[PySparseFC_Zero_NUM])
#define PySparseFC_Find \
  (*(PySparseFC_Find_RET (*)PySparseFC_Find_PROTO) \
   PyFF_API[PySparseFC_Find_NUM])
#define PySparseFC_AddTerm \
  (*(PySparseFC_AddTerm_RET (*)PySparseFC_AddTerm_PROTO) \
   PyFF_API[PySparseFC_AddTerm_NUM])
#define PySparseFC_CopyToArray \
  (*(PySparseFC_CopyToArray_RET (*)PySparseFC_CopyToArray_PROTO) \
   PyFF_API[PySparseFC_CopyToArray_NUM])
#define PySparseFC_AsArray \
  (*(PySparseFC_AsArray_RET (*)PySparseFC_AsArray_PROTO) \
   PyFF_API[PySparseFC_AsArray_NUM])
#define PySparseFC_VectorMultiply \
  (*(PySparseFC_VectorMultiply_RET (*)PySparseFC_VectorMultiply_PROTO) \
   PyFF_API[PySparseFC_VectorMultiply_NUM])
#define PyFFEnergyTerm_New \
  (*(PyFFEnergyTerm_New_RET (*)PyFFEnergyTerm_New_PROTO) \
   PyFF_API[PyFFEnergyTerm_New_NUM])
#define PyFFEvaluator_New \
  (*(PyFFEvaluator_New_RET (*)PyFFEvaluator_New_PROTO) \
   PyFF_API[PyFFEvaluator_New_NUM])
#define PySparseFC_Scale \
  (*(PySparseFC_Scale_RET (*)PySparseFC_Scale_PROTO) \
   PyFF_API[PySparseFC_Scale_NUM])
#define PyNonbondedListUpdate \
  (*(PyNonbondedListUpdate_RET (*)PyNonbondedListUpdate_PROTO) \
   PyFF_API[PyNonbondedListUpdate_NUM])
#define PyNonbondedListIterate \
  (*(PyNonbondedListIterate_RET (*)PyNonbondedListIterate_PROTO) \
   PyFF_API[PyNonbondedListIterate_NUM])

#endif

/* Import macro */
#define import_MMTK_forcefield() \
{ \
  PyObject *module = PyImport_ImportModule("MMTK_forcefield"); \
  if (module != NULL) { \
    PyObject *module_dict = PyModule_GetDict(module); \
    PyObject *c_api_object = PyDict_GetItemString(module_dict, "_C_API"); \
    if (PyCObject_Check(c_api_object)) { \
      PyFF_API = (void **)PyCObject_AsVoidPtr(c_api_object); \
    } \
  } \
}

#define MMTK_FORCEFIELD_H
#endif
