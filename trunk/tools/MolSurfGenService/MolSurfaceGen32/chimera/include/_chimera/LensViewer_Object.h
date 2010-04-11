#ifndef chimera_LensViewer_object_h
# define chimera_LensViewer_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "LensViewer.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject LensViewer_objectType;

struct LensViewer_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	LensViewer* _inst() { return static_cast<LensViewer*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern LensViewer* getInst(LensViewer_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::LensViewer>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::LensViewer_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::LensViewer* _o);
template <> inline PyObject* pyObject(chimera::LensViewer const* _o) { return pyObject(const_cast<chimera::LensViewer*>(_o)); }

} // namespace otf

#endif
