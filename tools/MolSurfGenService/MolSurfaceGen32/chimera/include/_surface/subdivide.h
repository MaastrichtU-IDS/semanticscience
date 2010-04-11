// ----------------------------------------------------------------------------
//
#ifndef SUBDIVIDE_HEADER_INCLUDED
#define SUBDIVIDE_HEADER_INCLUDED

#include <Python.h>			// use PyObject

#include "surfmodel_config.h"		// use SURFMODEL_IMEX

namespace Surface_Display
{
//
// Returns new vertex and triangle arrays where every triangle has been
// subdivided into 4 triangles by joining the original triangle edge
// mid-points.  One midpoint is made for each edge, even if more than
// one triangle borders that edge.  If normals are provide they are also
// averaged to make normals at new vertices and a new normals array is
// returned.
//
SURFMODEL_IMEX PyObject *subdivide_triangles(PyObject *vertex_array,
					     PyObject *triangle_array,
					     PyObject *normals_array = NULL);

//
// Subdivides triangles to achieve uniform edge length.
//
SURFMODEL_IMEX PyObject *subdivide_mesh(PyObject *vertex_array,
					PyObject *triangle_array,
					PyObject *normals_array,
					float edge_length);

}	// end of namespace Surface_Display

#endif
