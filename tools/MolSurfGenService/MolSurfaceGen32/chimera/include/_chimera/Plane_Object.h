#ifndef chimera_Plane_object_h
# define chimera_Plane_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Plane.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Plane_objectType;

struct Plane_object: public PyObject {
	PyObject* _inst_dict;
	double _inst_data[(sizeof (Plane) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	Plane* _inst() { return reinterpret_cast<Plane*>(_inst_data); }
};

CHIMERA_IMEX extern Plane* getInst(Plane_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Plane>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Plane_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Plane* _o);
template <> inline PyObject* pyObject(chimera::Plane _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(chimera::Plane const* _o) { return pyObject(const_cast<chimera::Plane*>(_o)); }

} // namespace otf

#endif
