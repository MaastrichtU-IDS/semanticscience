#ifndef chimera_RibbonStyleTapered_object_h
# define chimera_RibbonStyleTapered_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject RibbonStyleTapered_objectType;

struct RibbonStyleTapered_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	RibbonStyleTapered* _inst() { return static_cast<RibbonStyleTapered*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern RibbonStyleTapered* getInst(RibbonStyleTapered_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::RibbonStyleTapered>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::RibbonStyleTapered_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::RibbonStyleTapered* _o);
template <> inline PyObject* pyObject(chimera::RibbonStyleTapered const* _o) { return pyObject(const_cast<chimera::RibbonStyleTapered*>(_o)); }

} // namespace otf

#endif
