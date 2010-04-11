#ifndef chimera_PDBio_object_h
# define chimera_PDBio_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject PDBio_objectType;

struct PDBio_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	PDBio* _inst() { return static_cast<PDBio*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern PDBio* getInst(PDBio_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::PDBio>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::PDBio_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::PDBio* _o);
template <> inline PyObject* pyObject(chimera::PDBio const* _o) { return pyObject(const_cast<chimera::PDBio*>(_o)); }

} // namespace otf

#endif
