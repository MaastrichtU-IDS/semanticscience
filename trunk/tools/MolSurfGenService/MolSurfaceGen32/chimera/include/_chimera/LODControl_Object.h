#ifndef chimera_LODControl_object_h
# define chimera_LODControl_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "LODControl.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject LODControl_objectType;

struct LODControl_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	LODControl* _inst() { return static_cast<LODControl*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern LODControl* getInst(LODControl_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::LODControl>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::LODControl_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::LODControl* _o);
template <> inline PyObject* pyObject(chimera::LODControl const* _o) { return pyObject(const_cast<chimera::LODControl*>(_o)); }

} // namespace otf

#endif
