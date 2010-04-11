#ifndef chimera_Root_object_h
# define chimera_Root_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Root_objectType;

struct Root_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Root* _inst() { return static_cast<Root*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Root* getInst(Root_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Root>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Root_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Root* _o);
template <> inline PyObject* pyObject(chimera::Root const* _o) { return pyObject(const_cast<chimera::Root*>(_o)); }

} // namespace otf

#endif
