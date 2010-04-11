#ifndef chimera_TmplAtom_object_h
# define chimera_TmplAtom_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "TmplAtom.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject TmplAtom_objectType;

struct TmplAtom_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	TmplAtom* _inst() { return static_cast<TmplAtom*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern TmplAtom* getInst(TmplAtom_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::TmplAtom>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::TmplAtom_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::TmplAtom* _o);
template <> inline PyObject* pyObject(chimera::TmplAtom const* _o) { return pyObject(const_cast<chimera::TmplAtom*>(_o)); }

} // namespace otf

#endif
