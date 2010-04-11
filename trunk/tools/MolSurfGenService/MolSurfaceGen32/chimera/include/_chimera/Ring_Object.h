#ifndef chimera_Ring_object_h
# define chimera_Ring_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Ring_objectType;

struct Ring_object: public PyObject {
	PyObject* _inst_dict;
	double _inst_data[(sizeof (Ring) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	Ring* _inst() { return reinterpret_cast<Ring*>(_inst_data); }
};

CHIMERA_IMEX extern Ring* getInst(Ring_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Ring>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Ring_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Ring* _o);
template <> inline PyObject* pyObject(chimera::Ring _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(chimera::Ring const* _o) { return pyObject(const_cast<chimera::Ring*>(_o)); }

} // namespace otf

#endif
