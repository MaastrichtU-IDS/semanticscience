#ifndef chimera_Point_object_h
# define chimera_Point_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include <otf/Geom3d.h>
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Point_objectType;

struct Point_object: public PyObject {
	PyObject* _inst_dict;
	double _inst_data[(sizeof (otf::Geom3d::Point) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	otf::Geom3d::Point* _inst() { return reinterpret_cast<otf::Geom3d::Point*>(_inst_data); }
};

CHIMERA_IMEX extern otf::Geom3d::Point* getInst(Point_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<otf::Geom3d::Point>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Point_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(otf::Geom3d::Point* _o);
template <> inline PyObject* pyObject(otf::Geom3d::Point _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(otf::Geom3d::Point const* _o) { return pyObject(const_cast<otf::Geom3d::Point*>(_o)); }

} // namespace otf

#endif
