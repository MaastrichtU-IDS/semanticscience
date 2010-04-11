#ifndef chimera_Lens_object_h
# define chimera_Lens_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Lens.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Lens_objectType;

// help subclasses initialize cached attributes
CHIMERA_IMEX extern PyObject* Lens_attrInitmodels(PyObject*, void*);
CHIMERA_IMEX extern PyObject* Lens_attrInitsublenses(PyObject*, void*);

struct Lens_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Lens* _inst() { return static_cast<Lens*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Lens* getInst(Lens_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Lens>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Lens_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Lens* _o);
template <> inline PyObject* pyObject(chimera::Lens const* _o) { return pyObject(const_cast<chimera::Lens*>(_o)); }

} // namespace otf

#endif
