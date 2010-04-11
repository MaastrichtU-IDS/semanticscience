#ifndef chimera_PseudoBond_object_h
# define chimera_PseudoBond_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject PseudoBond_objectType;

struct PseudoBond_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	PseudoBond* _inst() { return static_cast<PseudoBond*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern PseudoBond* getInst(PseudoBond_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::PseudoBond>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::PseudoBond_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::PseudoBond* _o);
template <> inline PyObject* pyObject(chimera::PseudoBond const* _o) { return pyObject(const_cast<chimera::PseudoBond*>(_o)); }

} // namespace otf

#endif
