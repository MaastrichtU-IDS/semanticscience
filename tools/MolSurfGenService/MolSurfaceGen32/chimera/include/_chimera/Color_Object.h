#ifndef chimera_Color_object_h
# define chimera_Color_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Color.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Color_objectType;

struct Color_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Color* _inst() { return static_cast<Color*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Color* getInst(Color_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Color>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Color_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Color* _o);
template <> inline PyObject* pyObject(chimera::Color const* _o) { return pyObject(const_cast<chimera::Color*>(_o)); }
template <> inline PyObject* pyObject(chimera::Name<chimera::Color>* o) { return pyObject(static_cast<chimera::Color*>(o)); }

} // namespace otf

#endif
