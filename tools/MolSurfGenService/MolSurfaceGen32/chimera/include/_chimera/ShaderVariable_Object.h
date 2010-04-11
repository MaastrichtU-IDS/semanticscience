#ifndef chimera_ShaderVariable_object_h
# define chimera_ShaderVariable_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Shader.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject ShaderVariable_objectType;

struct ShaderVariable_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	ShaderVariable* _inst() { return static_cast<ShaderVariable*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern ShaderVariable* getInst(ShaderVariable_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::ShaderVariable>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::ShaderVariable_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::ShaderVariable* _o);
template <> inline PyObject* pyObject(chimera::ShaderVariable const* _o) { return pyObject(const_cast<chimera::ShaderVariable*>(_o)); }

} // namespace otf

#endif
