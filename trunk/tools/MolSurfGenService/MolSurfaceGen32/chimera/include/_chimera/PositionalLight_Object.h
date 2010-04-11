#ifndef chimera_PositionalLight_object_h
# define chimera_PositionalLight_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Light.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject PositionalLight_objectType;

struct PositionalLight_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	PositionalLight* _inst() { return static_cast<PositionalLight*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern PositionalLight* getInst(PositionalLight_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::PositionalLight>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::PositionalLight_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::PositionalLight* _o);
template <> inline PyObject* pyObject(chimera::PositionalLight const* _o) { return pyObject(const_cast<chimera::PositionalLight*>(_o)); }

} // namespace otf

#endif
