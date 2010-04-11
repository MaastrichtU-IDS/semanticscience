// ----------------------------------------------------------------------------
//
#ifndef SQUAREMESH_HEADER_INCLUDED
#define SQUAREMESH_HEADER_INCLUDED

#include <Python.h>			// use PyObject

#include "surfmodel_config.h"		// use SURFMODEL_IMEX

namespace Surface_Display
{
//
// Return integer array having length equal to length of triangle array
// with bit values indicating which edges that are parallel to one of the
// principle planes (xy, yz and xz).
//
// The returned array is for use as an argument to Surface_Renderer
// set_triangle_and_edge_mask().
//
SURFMODEL_IMEX PyObject *principle_plane_edges(PyObject *vertex_array,
					       PyObject *triangle_array);

}	// end of namespace Surface_Display

#endif
