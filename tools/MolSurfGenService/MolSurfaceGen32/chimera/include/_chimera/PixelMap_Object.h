#ifndef chimera_PixelMap_object_h
# define chimera_PixelMap_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "PixelMap.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject PixelMap_objectType;

struct PixelMap_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	PixelMap* _inst() { return static_cast<PixelMap*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern PixelMap* getInst(PixelMap_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::PixelMap>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::PixelMap_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::PixelMap* _o);
template <> inline PyObject* pyObject(chimera::PixelMap const* _o) { return pyObject(const_cast<chimera::PixelMap*>(_o)); }
template <> inline PyObject* pyObject(chimera::Name<chimera::PixelMap>* o) { return pyObject(static_cast<chimera::PixelMap*>(o)); }

} // namespace otf

#endif
