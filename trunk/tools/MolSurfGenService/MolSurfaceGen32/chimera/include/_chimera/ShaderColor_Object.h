#ifndef chimera_ShaderColor_object_h
# define chimera_ShaderColor_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "ShaderColor.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject ShaderColor_objectType;

struct ShaderColor_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	ShaderColor* _inst() { return static_cast<ShaderColor*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern ShaderColor* getInst(ShaderColor_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::ShaderColor>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::ShaderColor_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::ShaderColor* _o);
template <> inline PyObject* pyObject(chimera::ShaderColor const* _o) { return pyObject(const_cast<chimera::ShaderColor*>(_o)); }

} // namespace otf

#endif
