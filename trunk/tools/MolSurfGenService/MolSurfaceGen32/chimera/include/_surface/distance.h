// ----------------------------------------------------------------------------
//
#ifndef SURFDIST_HEADER_INCLUDED
#define SURFDIST_HEADER_INCLUDED

#include <Python.h>			// use PyObject

#include "surfmodel_config.h"		// use SURFMODEL_IMEX

namespace Surface_Display
{
//
// Compute the closest distance from a point to a surface.  Do this for
// each point in a list.  The distance, closest point, and side of the closest
// triangle that the given point lies on is returned in an N by 5 float32 array.
// Side +1 is the right-handed normal clockwise vertex traversal, while -1
// indicates the opposite side.  This is for determining if the given point
// is inside or outside the surface.  If a distance array (N by 5) is passed
// as an argument, it will only be modified by distances less those.  If no
// distance array is provided, a newly allocated one will be returned.
//
SURFMODEL_IMEX PyObject *surface_distance(PyObject *points,
					  PyObject *vertex_array,
					  PyObject *triangle_array,
					  PyObject *distances = NULL);

}	// end of namespace Surface_Display

#endif
