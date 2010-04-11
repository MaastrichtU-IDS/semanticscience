#ifndef chimera_DirectionalLight_object_h
# define chimera_DirectionalLight_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Light.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject DirectionalLight_objectType;

struct DirectionalLight_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	DirectionalLight* _inst() { return static_cast<DirectionalLight*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern DirectionalLight* getInst(DirectionalLight_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::DirectionalLight>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::DirectionalLight_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::DirectionalLight* _o);
template <> inline PyObject* pyObject(chimera::DirectionalLight const* _o) { return pyObject(const_cast<chimera::DirectionalLight*>(_o)); }

} // namespace otf

#endif
