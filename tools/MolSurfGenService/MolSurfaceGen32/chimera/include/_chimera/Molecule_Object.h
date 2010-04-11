#ifndef chimera_Molecule_object_h
# define chimera_Molecule_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Molecule_objectType;

struct Molecule_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Molecule* _inst() { return static_cast<Molecule*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Molecule* getInst(Molecule_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Molecule>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Molecule_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Molecule* _o);
template <> inline PyObject* pyObject(chimera::Molecule const* _o) { return pyObject(const_cast<chimera::Molecule*>(_o)); }

} // namespace otf

#endif
