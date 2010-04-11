#ifndef chimera_RibbonStyleFixed_object_h
# define chimera_RibbonStyleFixed_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject RibbonStyleFixed_objectType;

struct RibbonStyleFixed_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	RibbonStyleFixed* _inst() { return static_cast<RibbonStyleFixed*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern RibbonStyleFixed* getInst(RibbonStyleFixed_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::RibbonStyleFixed>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::RibbonStyleFixed_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::RibbonStyleFixed* _o);
template <> inline PyObject* pyObject(chimera::RibbonStyleFixed const* _o) { return pyObject(const_cast<chimera::RibbonStyleFixed*>(_o)); }

} // namespace otf

#endif
