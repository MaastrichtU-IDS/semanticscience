#ifndef chimera_MaterialColor_object_h
# define chimera_MaterialColor_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "MaterialColor.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject MaterialColor_objectType;

struct MaterialColor_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	MaterialColor* _inst() { return static_cast<MaterialColor*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern MaterialColor* getInst(MaterialColor_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::MaterialColor>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::MaterialColor_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::MaterialColor* _o);
template <> inline PyObject* pyObject(chimera::MaterialColor const* _o) { return pyObject(const_cast<chimera::MaterialColor*>(_o)); }

} // namespace otf

#endif
