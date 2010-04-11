// ----------------------------------------------------------------------------
//
#ifndef CONNECTED_HEADER_INCLUDED
#define CONNECTED_HEADER_INCLUDED

#include <Python.h>			// use PyObject

#include "surfmodel_config.h"		// use SURFMODEL_IMEX

namespace Surface_Display
{
//
// Return sorted array of triangle indices of triangles connected to the
// specified triangle.  Two triangles are connected if they share a vertex.
// The surface must be oriented and at most two triangles can share an edge.
// The triangle array is triples of indices of vertices (m by 3, Numpy int32).
//
SURFMODEL_IMEX PyObject *connected_triangles(PyObject *triangle_array,
					     int tindex);
SURFMODEL_IMEX PyObject *triangle_vertices(PyObject *triagle_array,
					   PyObject *triangle_list);

//
// Return each connected piece of a surface as a separate triangle array
// and vertex array.  The return value is a tuple of pairs of vertex and
// triangle index arrays.  Vertices connected by any sequence of triangle
// edges are considered connected.
//
SURFMODEL_IMEX PyObject *connected_pieces(PyObject *triangle_array);

}	// end of namespace Surface_Display

#endif
