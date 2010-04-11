#ifndef chimera_GeometryVector_object_h
# define chimera_GeometryVector_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Spline.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject GeometryVector_objectType;

struct GeometryVector_object: public PyObject {
	PyObject* _inst_dict;
	double _inst_data[(sizeof (GeometryVector) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	GeometryVector* _inst() { return reinterpret_cast<GeometryVector*>(_inst_data); }
};

CHIMERA_IMEX extern GeometryVector* getInst(GeometryVector_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::GeometryVector>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::GeometryVector_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::GeometryVector* _o);
template <> inline PyObject* pyObject(chimera::GeometryVector _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(chimera::GeometryVector const* _o) { return pyObject(const_cast<chimera::GeometryVector*>(_o)); }

} // namespace otf

#endif
