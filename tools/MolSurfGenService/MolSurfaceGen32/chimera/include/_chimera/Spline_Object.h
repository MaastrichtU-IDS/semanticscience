#ifndef chimera_Spline_object_h
# define chimera_Spline_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Spline.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Spline_objectType;

struct Spline_object: public PyObject {
	PyObject* _inst_dict;
	Spline* _inst_data;
	Spline* _inst() { return _inst_data; }
};

CHIMERA_IMEX extern Spline* getInst(Spline_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Spline>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Spline_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Spline* _o);
template <> inline PyObject* pyObject(chimera::Spline const* _o) { return pyObject(const_cast<chimera::Spline*>(_o)); }

} // namespace otf

#endif
