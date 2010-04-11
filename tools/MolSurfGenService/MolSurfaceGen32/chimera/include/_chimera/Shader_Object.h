#ifndef chimera_Shader_object_h
# define chimera_Shader_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Shader.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Shader_objectType;

struct Shader_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Shader* _inst() { return static_cast<Shader*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Shader* getInst(Shader_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Shader>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Shader_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Shader* _o);
template <> inline PyObject* pyObject(chimera::Shader const* _o) { return pyObject(const_cast<chimera::Shader*>(_o)); }
template <> inline PyObject* pyObject(chimera::Name<chimera::Shader>* o) { return pyObject(static_cast<chimera::Shader*>(o)); }

} // namespace otf

#endif
