#ifndef Surface_Display_SurfacePiece_object_h
# define Surface_Display_SurfacePiece_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "surfmodel.h"
#include <otf/WrapPy2.h>
namespace Surface_Display {

SURFMODEL_IMEX extern PyTypeObject SurfacePiece_objectType;

struct SurfacePiece_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	SurfacePiece* _inst() { return static_cast<SurfacePiece*>(_inst_data); }
	PyObject* _weaklist;
};

SURFMODEL_IMEX extern SurfacePiece* getInst(SurfacePiece_object* self);

} // namespace Surface_Display

namespace otf {

template <> inline bool
WrapPyType<Surface_Display::SurfacePiece>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &Surface_Display::SurfacePiece_objectType);
}

template <> SURFMODEL_IMEX PyObject* pyObject(Surface_Display::SurfacePiece* _o);
template <> inline PyObject* pyObject(Surface_Display::SurfacePiece const* _o) { return pyObject(const_cast<Surface_Display::SurfacePiece*>(_o)); }

} // namespace otf

#endif
