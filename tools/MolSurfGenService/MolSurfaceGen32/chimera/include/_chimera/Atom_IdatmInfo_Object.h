#ifndef chimera_Atom_IdatmInfo_object_h
# define chimera_Atom_IdatmInfo_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Atom_IdatmInfo_objectType;

struct Atom_IdatmInfo_object: public PyObject {
	double _inst_data[(sizeof (Atom::IdatmInfo) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	Atom::IdatmInfo* _inst() { return reinterpret_cast<Atom::IdatmInfo*>(_inst_data); }
};

CHIMERA_IMEX extern Atom::IdatmInfo* getInst(Atom_IdatmInfo_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Atom::IdatmInfo>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Atom_IdatmInfo_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Atom::IdatmInfo* _o);
template <> inline PyObject* pyObject(chimera::Atom::IdatmInfo _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(chimera::Atom::IdatmInfo const* _o) { return pyObject(const_cast<chimera::Atom::IdatmInfo*>(_o)); }

} // namespace otf

#endif
