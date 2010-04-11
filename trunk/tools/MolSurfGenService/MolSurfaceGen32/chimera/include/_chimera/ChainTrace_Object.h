#ifndef chimera_ChainTrace_object_h
# define chimera_ChainTrace_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject ChainTrace_objectType;

struct ChainTrace_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	ChainTrace* _inst() { return static_cast<ChainTrace*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern ChainTrace* getInst(ChainTrace_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::ChainTrace>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::ChainTrace_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::ChainTrace* _o);
template <> inline PyObject* pyObject(chimera::ChainTrace const* _o) { return pyObject(const_cast<chimera::ChainTrace*>(_o)); }

} // namespace otf

#endif
