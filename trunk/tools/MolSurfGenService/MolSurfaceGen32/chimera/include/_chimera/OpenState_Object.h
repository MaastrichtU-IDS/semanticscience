#ifndef chimera_OpenState_object_h
# define chimera_OpenState_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "OpenModels.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject OpenState_objectType;

struct OpenState_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	OpenState* _inst() { return static_cast<OpenState*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern OpenState* getInst(OpenState_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::OpenState>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::OpenState_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::OpenState* _o);
template <> inline PyObject* pyObject(chimera::OpenState const* _o) { return pyObject(const_cast<chimera::OpenState*>(_o)); }

} // namespace otf

#endif
