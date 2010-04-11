#ifndef chimera_PseudoBondGroup_object_h
# define chimera_PseudoBondGroup_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject PseudoBondGroup_objectType;

struct PseudoBondGroup_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	PseudoBondGroup* _inst() { return static_cast<PseudoBondGroup*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern PseudoBondGroup* getInst(PseudoBondGroup_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::PseudoBondGroup>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::PseudoBondGroup_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::PseudoBondGroup* _o);
template <> inline PyObject* pyObject(chimera::PseudoBondGroup const* _o) { return pyObject(const_cast<chimera::PseudoBondGroup*>(_o)); }

} // namespace otf

#endif
