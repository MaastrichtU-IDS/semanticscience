#ifndef Surface_Display_SurfaceModel_object_h
# define Surface_Display_SurfaceModel_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "surfmodel.h"
#include <otf/WrapPy2.h>
namespace Surface_Display {

SURFMODEL_IMEX extern PyTypeObject SurfaceModel_objectType;

// help subclasses initialize cached attributes
SURFMODEL_IMEX extern PyObject* SurfaceModel_attrInitmaterial(PyObject*, void*);
SURFMODEL_IMEX extern PyObject* SurfaceModel_attrInitsurfacePieces(PyObject*, void*);

struct SurfaceModel_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	SurfaceModel* _inst() { return static_cast<SurfaceModel*>(_inst_data); }
	PyObject* _weaklist;
};

SURFMODEL_IMEX extern SurfaceModel* getInst(SurfaceModel_object* self);

} // namespace Surface_Display

namespace otf {

template <> inline bool
WrapPyType<Surface_Display::SurfaceModel>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &Surface_Display::SurfaceModel_objectType);
}

template <> SURFMODEL_IMEX PyObject* pyObject(Surface_Display::SurfaceModel* _o);
template <> inline PyObject* pyObject(Surface_Display::SurfaceModel const* _o) { return pyObject(const_cast<Surface_Display::SurfaceModel*>(_o)); }

} // namespace otf

#endif
