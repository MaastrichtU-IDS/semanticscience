#ifndef chimera_RibbonResidueClass_object_h
# define chimera_RibbonResidueClass_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject RibbonResidueClass_objectType;

struct RibbonResidueClass_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	RibbonResidueClass* _inst() { return static_cast<RibbonResidueClass*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern RibbonResidueClass* getInst(RibbonResidueClass_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::RibbonResidueClass>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::RibbonResidueClass_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::RibbonResidueClass* _o);
template <> inline PyObject* pyObject(chimera::RibbonResidueClass const* _o) { return pyObject(const_cast<chimera::RibbonResidueClass*>(_o)); }

} // namespace otf

#endif
