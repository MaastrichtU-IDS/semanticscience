// ----------------------------------------------------------------------------
//
#ifndef NORMALS_HEADER_INCLUDED
#define NORMALS_HEADER_INCLUDED

#include <Python.h>			// use PyObject

#include "rcarray.h"			// use FArray, IArray
#include "surfmodel_config.h"		// use SURFMODEL_IMEX

namespace Surface_Display
{

#ifndef WrapPy
SURFMODEL_IMEX FArray calculate_vertex_normals(const FArray &vertices,
					       const IArray &triangles);
SURFMODEL_IMEX void invert_vertex_normals(const FArray &normals,
					  const IArray &triangles);
#endif

SURFMODEL_IMEX PyObject *calculate_vertex_normals(PyObject *vertex_array,
						  PyObject *triangle_array);
SURFMODEL_IMEX PyObject *invert_vertex_normals(PyObject *normals_array,
					       PyObject *triangle_array);

}	// end of namespace Surface_Display

#endif
