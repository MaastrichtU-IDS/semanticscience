#ifndef chimera_Sphere_object_h
# define chimera_Sphere_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "sphere.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Sphere_objectType;

struct Sphere_object: public PyObject {
	PyObject* _inst_dict;
	double _inst_data[(sizeof (Sphere) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	Sphere* _inst() { return reinterpret_cast<Sphere*>(_inst_data); }
};

CHIMERA_IMEX extern Sphere* getInst(Sphere_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Sphere>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Sphere_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Sphere* _o);
template <> inline PyObject* pyObject(chimera::Sphere _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(chimera::Sphere const* _o) { return pyObject(const_cast<chimera::Sphere*>(_o)); }

} // namespace otf

#endif
