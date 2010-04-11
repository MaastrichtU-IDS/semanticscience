#ifndef chimera_Viewer_object_h
# define chimera_Viewer_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Viewer.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Viewer_objectType;

// help subclasses initialize cached attributes
CHIMERA_IMEX extern PyObject* Viewer_attrInitbackground(PyObject*, void*);
CHIMERA_IMEX extern PyObject* Viewer_attrInitcamera(PyObject*, void*);

struct Viewer_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Viewer* _inst() { return static_cast<Viewer*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Viewer* getInst(Viewer_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Viewer>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Viewer_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Viewer* _o);
template <> inline PyObject* pyObject(chimera::Viewer const* _o) { return pyObject(const_cast<chimera::Viewer*>(_o)); }

} // namespace otf

#endif
