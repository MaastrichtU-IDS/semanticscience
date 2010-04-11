#ifndef chimera_CoordSet_object_h
# define chimera_CoordSet_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject CoordSet_objectType;

struct CoordSet_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	CoordSet* _inst() { return static_cast<CoordSet*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern CoordSet* getInst(CoordSet_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::CoordSet>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::CoordSet_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::CoordSet* _o);
template <> inline PyObject* pyObject(chimera::CoordSet const* _o) { return pyObject(const_cast<chimera::CoordSet*>(_o)); }

} // namespace otf

#endif
