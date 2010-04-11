#ifndef chimera_X3DScene_object_h
# define chimera_X3DScene_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "X3DScene.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject X3DScene_objectType;

struct X3DScene_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	X3DScene* _inst() { return static_cast<X3DScene*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern X3DScene* getInst(X3DScene_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::X3DScene>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::X3DScene_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::X3DScene* _o);
template <> inline PyObject* pyObject(chimera::X3DScene const* _o) { return pyObject(const_cast<chimera::X3DScene*>(_o)); }

} // namespace otf

#endif
