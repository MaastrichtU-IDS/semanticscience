#ifndef chimera_PseudoBondMgr_object_h
# define chimera_PseudoBondMgr_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject PseudoBondMgr_objectType;

struct PseudoBondMgr_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	PseudoBondMgr* _inst() { return static_cast<PseudoBondMgr*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern PseudoBondMgr* getInst(PseudoBondMgr_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::PseudoBondMgr>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::PseudoBondMgr_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::PseudoBondMgr* _o);
template <> inline PyObject* pyObject(chimera::PseudoBondMgr const* _o) { return pyObject(const_cast<chimera::PseudoBondMgr*>(_o)); }

} // namespace otf

#endif
