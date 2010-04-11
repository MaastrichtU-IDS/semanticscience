/* Private include file for C force field calculations.
 *
 * Written by Konrad Hinsen
 * last revision: 2007-4-24
 */

#ifndef MMTK_FORCEFIELD_PRIVATE_H

#include "MMTK/universe.h"

#undef GRADIENTFN

/* Global variables */

extern distance_fn *distance_vector_pointer;
extern distance_fn *orthorhombic_distance_vector_pointer;
extern distance_fn *parallelepipedic_distance_vector_pointer;

/* Functions in MMTK/forcefieldmodule.c */

void
add_pair_fc(energy_data *energy, int i, int j, vector3 dr,
	    double r_sq, double f1, double f2);

#ifdef WITH_THREAD

/* Remove a macro from Linux 2.6 that is in the way */
#ifdef barrier
#undef barrier
#endif

void
barrier(barrierinfo *binfo, int thread_id, int nthreads);
#endif

/* Functions in bonded.c */

ff_eterm_function harmonic_bond_evaluator;
ff_eterm_function harmonic_angle_evaluator;
ff_eterm_function cosine_dihedral_evaluator;


/* Functions in nonbonded.c */

int
nblist_update(PyNonbondedListObject *nblist, int natoms,
	      double *coordinates, double *geometry_data);
int
nblist_iterate(PyNonbondedListObject *nblist,
	       struct nblist_iterator *iterator);

ff_eterm_function nonbonded_evaluator;
ff_eterm_function lennard_jones_evaluator;
ff_eterm_function electrostatic_evaluator;
ff_eterm_function es_mp_evaluator;
ff_eterm_function lj_es_evaluator;
ff_eterm_function es_ewald_evaluator;


/* Functions in ewald.c */

int
init_kvectors(box_fn *box_transformation_fn, double *universe_data, int natoms,
	      long *kmax, double cutoff_sq, void *scratch, int nvect);

/* Functions in sparsefc.c */

PyObject *
SparseForceConstants(PyObject *dummy, PyObject *args);

fc_function sparse_fc_function;

#define MMTK_FORCEFIELD_PRIVATE_H
#endif
