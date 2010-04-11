#ifndef chimera_Residue_object_h
# define chimera_Residue_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Residue_objectType;

struct Residue_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Residue* _inst() { return static_cast<Residue*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Residue* getInst(Residue_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Residue>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Residue_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Residue* _o);
template <> inline PyObject* pyObject(chimera::Residue const* _o) { return pyObject(const_cast<chimera::Residue*>(_o)); }

} // namespace otf

#endif
