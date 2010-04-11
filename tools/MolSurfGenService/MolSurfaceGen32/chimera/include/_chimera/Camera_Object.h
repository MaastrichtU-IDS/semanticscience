#ifndef chimera_Camera_object_h
# define chimera_Camera_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Camera.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Camera_objectType;

struct Camera_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Camera* _inst() { return static_cast<Camera*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Camera* getInst(Camera_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Camera>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Camera_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Camera* _o);
template <> inline PyObject* pyObject(chimera::Camera const* _o) { return pyObject(const_cast<chimera::Camera*>(_o)); }

} // namespace otf

#endif
