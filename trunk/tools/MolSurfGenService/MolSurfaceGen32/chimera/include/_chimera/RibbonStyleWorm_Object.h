#ifndef chimera_RibbonStyleWorm_object_h
# define chimera_RibbonStyleWorm_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject RibbonStyleWorm_objectType;

struct RibbonStyleWorm_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	RibbonStyleWorm* _inst() { return static_cast<RibbonStyleWorm*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern RibbonStyleWorm* getInst(RibbonStyleWorm_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::RibbonStyleWorm>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::RibbonStyleWorm_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::RibbonStyleWorm* _o);
template <> inline PyObject* pyObject(chimera::RibbonStyleWorm const* _o) { return pyObject(const_cast<chimera::RibbonStyleWorm*>(_o)); }

} // namespace otf

#endif
