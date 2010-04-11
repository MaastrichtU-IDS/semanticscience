#ifndef chimera_BondRot_object_h
# define chimera_BondRot_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject BondRot_objectType;

struct BondRot_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	BondRot* _inst() { return static_cast<BondRot*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern BondRot* getInst(BondRot_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::BondRot>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::BondRot_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::BondRot* _o);
template <> inline PyObject* pyObject(chimera::BondRot const* _o) { return pyObject(const_cast<chimera::BondRot*>(_o)); }

} // namespace otf

#endif
