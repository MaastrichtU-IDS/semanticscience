// ----------------------------------------------------------------------------
//
#ifndef SMOOTH_HEADER_INCLUDED
#define SMOOTH_HEADER_INCLUDED

#include <Python.h>			// use PyObject

#include "surfmodel_config.h"		// use SURFMODEL_IMEX

namespace Surface_Display
{
//
// Move surface vertices towards the average of neighboring vertices
// give the surface a smoother appearance.
// The vertex array is xyz points (n by 3, NumPy C float).
// The triangle array is triples of indices into the vertex array.
//
SURFMODEL_IMEX void smooth_vertex_positions(PyObject *vertex_array,
					    PyObject *triangle_array,
					    float smoothing_factor,
					    int smoothing_iterations);
}	// end of namespace Surface_Display

#endif
