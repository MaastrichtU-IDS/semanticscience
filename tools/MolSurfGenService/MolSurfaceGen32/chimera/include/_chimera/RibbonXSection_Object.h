#ifndef chimera_RibbonXSection_object_h
# define chimera_RibbonXSection_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject RibbonXSection_objectType;

struct RibbonXSection_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	RibbonXSection* _inst() { return static_cast<RibbonXSection*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern RibbonXSection* getInst(RibbonXSection_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::RibbonXSection>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::RibbonXSection_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::RibbonXSection* _o);
template <> inline PyObject* pyObject(chimera::RibbonXSection const* _o) { return pyObject(const_cast<chimera::RibbonXSection*>(_o)); }

} // namespace otf

#endif
