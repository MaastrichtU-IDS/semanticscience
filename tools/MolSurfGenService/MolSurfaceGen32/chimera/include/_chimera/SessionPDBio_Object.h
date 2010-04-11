#ifndef chimera_SessionPDBio_object_h
# define chimera_SessionPDBio_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "SessionPDBio.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject SessionPDBio_objectType;

struct SessionPDBio_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	SessionPDBio* _inst() { return static_cast<SessionPDBio*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern SessionPDBio* getInst(SessionPDBio_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::SessionPDBio>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::SessionPDBio_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::SessionPDBio* _o);
template <> inline PyObject* pyObject(chimera::SessionPDBio const* _o) { return pyObject(const_cast<chimera::SessionPDBio*>(_o)); }

} // namespace otf

#endif
