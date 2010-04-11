#ifndef chimera_SpotLight_object_h
# define chimera_SpotLight_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Light.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject SpotLight_objectType;

struct SpotLight_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	SpotLight* _inst() { return static_cast<SpotLight*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern SpotLight* getInst(SpotLight_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::SpotLight>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::SpotLight_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::SpotLight* _o);
template <> inline PyObject* pyObject(chimera::SpotLight const* _o) { return pyObject(const_cast<chimera::SpotLight*>(_o)); }

} // namespace otf

#endif
