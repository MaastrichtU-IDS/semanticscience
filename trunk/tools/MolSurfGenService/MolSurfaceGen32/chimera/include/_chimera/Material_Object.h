#ifndef chimera_Material_object_h
# define chimera_Material_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Material.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Material_objectType;

struct Material_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Material* _inst() { return static_cast<Material*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Material* getInst(Material_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Material>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Material_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Material* _o);
template <> inline PyObject* pyObject(chimera::Material const* _o) { return pyObject(const_cast<chimera::Material*>(_o)); }
template <> inline PyObject* pyObject(chimera::Name<chimera::Material>* o) { return pyObject(static_cast<chimera::Material*>(o)); }

} // namespace otf

#endif
