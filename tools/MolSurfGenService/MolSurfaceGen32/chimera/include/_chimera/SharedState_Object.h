#ifndef chimera_SharedState_object_h
# define chimera_SharedState_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "SharedState.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject SharedState_objectType;

struct SharedState_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	SharedState* _inst() { return static_cast<SharedState*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern SharedState* getInst(SharedState_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::SharedState>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::SharedState_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::SharedState* _o);
template <> inline PyObject* pyObject(chimera::SharedState const* _o) { return pyObject(const_cast<chimera::SharedState*>(_o)); }

} // namespace otf

#endif
