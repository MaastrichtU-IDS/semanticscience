#ifndef chimera_ColorGroup_object_h
# define chimera_ColorGroup_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "ColorGroup.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject ColorGroup_objectType;

struct ColorGroup_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	ColorGroup* _inst() { return static_cast<ColorGroup*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern ColorGroup* getInst(ColorGroup_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::ColorGroup>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::ColorGroup_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::ColorGroup* _o);
template <> inline PyObject* pyObject(chimera::ColorGroup const* _o) { return pyObject(const_cast<chimera::ColorGroup*>(_o)); }

} // namespace otf

#endif
