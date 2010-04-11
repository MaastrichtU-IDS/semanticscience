// ----------------------------------------------------------------------------
//
#ifndef INTERCEPT_HEADER_INCLUDED
#define INTERCEPT_HEADER_INCLUDED

#include <Python.h>			// use PyObject

#include "surfmodel_config.h"		// use SURFMODEL_IMEX
#include "rcarray.h"			// use FArray, IArray

namespace Surface_Display
{
//
// Find closest triangle intercepting line segment between xyz1 and xyz2.
// The vertex array is xyz points (n by 3, NumPy single).
// The triangle array is triples of indices into the vertex array (m by 3,
// NumPy intc).
// Returns fraction of way along segment triangle index.
//
SURFMODEL_IMEX PyObject *closest_geometry_intercept(PyObject *vertex_array,
						    PyObject *triangle_array,
						    PyObject *xyz1,
						    PyObject *xyz2);

#ifndef WrapPy
bool closest_geometry_intercept(const FArray &varray, const IArray &tarray,
				const float xyz1[3], const float xyz2[3],
				float *fmin, int *tmin);
#endif

}	// end of namespace Surface_Display

#endif
