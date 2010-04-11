#ifndef chimera_OGLFont_object_h
# define chimera_OGLFont_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "OGLFont.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject OGLFont_objectType;

struct OGLFont_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	OGLFont* _inst() { return static_cast<OGLFont*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern OGLFont* getInst(OGLFont_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::OGLFont>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::OGLFont_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::OGLFont* _o);
template <> inline PyObject* pyObject(chimera::OGLFont const* _o) { return pyObject(const_cast<chimera::OGLFont*>(_o)); }

} // namespace otf

#endif
