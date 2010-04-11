// ----------------------------------------------------------------------------
//
#ifndef MEASURE_HEADER_INCLUDED
#define MEASURE_HEADER_INCLUDED

#include <Python.h>			// use PyObject

#include "surfmodel_config.h"		// use SURFMODEL_IMEX

namespace Surface_Display
{
// If surface has hole then returned volume is computed by capping
// boundary loops with fans centered at geometric center of loops.
SURFMODEL_IMEX float enclosed_volume(PyObject *vertex_array,
				     PyObject *triangle_array,
				     /*OUT*/ int *hole_count);

// Sum of triangle areas.
SURFMODEL_IMEX float surface_area(PyObject *vertex_array,
				  PyObject *triangle_array);

// Accumulate 1/3 triangle area to each vertex.
SURFMODEL_IMEX PyObject *vertex_areas(PyObject *vertex_array,
				      PyObject *triangle_array,
				      PyObject *areas = NULL);

// Returns N by 2 array of vertex indices for directed edges.
SURFMODEL_IMEX PyObject *boundary_edges(PyObject *triangle_array);

}	// end of namespace Surface_Display

#endif
