#ifndef chimera_RibbonData_object_h
# define chimera_RibbonData_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject RibbonData_objectType;

struct RibbonData_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	RibbonData* _inst() { return static_cast<RibbonData*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern RibbonData* getInst(RibbonData_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::RibbonData>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::RibbonData_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::RibbonData* _o);
template <> inline PyObject* pyObject(chimera::RibbonData const* _o) { return pyObject(const_cast<chimera::RibbonData*>(_o)); }

} // namespace otf

#endif
