#ifndef chimera_RibbonStyle_object_h
# define chimera_RibbonStyle_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject RibbonStyle_objectType;

struct RibbonStyle_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	RibbonStyle* _inst() { return static_cast<RibbonStyle*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern RibbonStyle* getInst(RibbonStyle_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::RibbonStyle>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::RibbonStyle_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::RibbonStyle* _o);
template <> inline PyObject* pyObject(chimera::RibbonStyle const* _o) { return pyObject(const_cast<chimera::RibbonStyle*>(_o)); }

} // namespace otf

#endif
