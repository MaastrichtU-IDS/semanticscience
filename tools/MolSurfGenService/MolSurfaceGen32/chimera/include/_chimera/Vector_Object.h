#ifndef chimera_Vector_object_h
# define chimera_Vector_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include <otf/Geom3d.h>
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Vector_objectType;

struct Vector_object: public PyObject {
	PyObject* _inst_dict;
	double _inst_data[(sizeof (otf::Geom3d::Vector) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	otf::Geom3d::Vector* _inst() { return reinterpret_cast<otf::Geom3d::Vector*>(_inst_data); }
};

CHIMERA_IMEX extern otf::Geom3d::Vector* getInst(Vector_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<otf::Geom3d::Vector>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Vector_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(otf::Geom3d::Vector* _o);
template <> inline PyObject* pyObject(otf::Geom3d::Vector _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(otf::Geom3d::Vector const* _o) { return pyObject(const_cast<otf::Geom3d::Vector*>(_o)); }

} // namespace otf

#endif
