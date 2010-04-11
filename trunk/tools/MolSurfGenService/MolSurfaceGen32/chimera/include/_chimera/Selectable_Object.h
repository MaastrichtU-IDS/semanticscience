#ifndef chimera_Selectable_object_h
# define chimera_Selectable_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Selectable.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Selectable_objectType;

struct Selectable_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Selectable* _inst() { return static_cast<Selectable*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Selectable* getInst(Selectable_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Selectable>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Selectable_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Selectable* _o);
template <> inline PyObject* pyObject(chimera::Selectable const* _o) { return pyObject(const_cast<chimera::Selectable*>(_o)); }

} // namespace otf

#endif
