#ifndef chimera_BBox_object_h
# define chimera_BBox_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include <otf/Geom3d.h>
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject BBox_objectType;

struct BBox_object: public PyObject {
	PyObject* _inst_dict;
	double _inst_data[(sizeof (otf::Geom3d::BBox) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	otf::Geom3d::BBox* _inst() { return reinterpret_cast<otf::Geom3d::BBox*>(_inst_data); }
};

CHIMERA_IMEX extern otf::Geom3d::BBox* getInst(BBox_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<otf::Geom3d::BBox>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::BBox_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(otf::Geom3d::BBox* _o);
template <> inline PyObject* pyObject(otf::Geom3d::BBox _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(otf::Geom3d::BBox const* _o) { return pyObject(const_cast<otf::Geom3d::BBox*>(_o)); }

} // namespace otf

#endif
