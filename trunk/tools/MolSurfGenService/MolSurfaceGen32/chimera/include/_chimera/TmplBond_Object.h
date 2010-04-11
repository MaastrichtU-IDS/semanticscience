#ifndef chimera_TmplBond_object_h
# define chimera_TmplBond_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "TmplBond.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject TmplBond_objectType;

struct TmplBond_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	TmplBond* _inst() { return static_cast<TmplBond*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern TmplBond* getInst(TmplBond_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::TmplBond>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::TmplBond_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::TmplBond* _o);
template <> inline PyObject* pyObject(chimera::TmplBond const* _o) { return pyObject(const_cast<chimera::TmplBond*>(_o)); }

} // namespace otf

#endif
