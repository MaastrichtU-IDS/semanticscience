#ifndef chimera_TmplResidue_object_h
# define chimera_TmplResidue_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "TmplResidue.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject TmplResidue_objectType;

struct TmplResidue_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	TmplResidue* _inst() { return static_cast<TmplResidue*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern TmplResidue* getInst(TmplResidue_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::TmplResidue>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::TmplResidue_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::TmplResidue* _o);
template <> inline PyObject* pyObject(chimera::TmplResidue const* _o) { return pyObject(const_cast<chimera::TmplResidue*>(_o)); }

} // namespace otf

#endif
