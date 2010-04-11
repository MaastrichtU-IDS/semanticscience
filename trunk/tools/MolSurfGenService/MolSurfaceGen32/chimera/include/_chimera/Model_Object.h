#ifndef chimera_Model_object_h
# define chimera_Model_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Model.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Model_objectType;

// help subclasses initialize cached attributes
CHIMERA_IMEX extern PyObject* Model_attrInitcolor(PyObject*, void*);

struct Model_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Model* _inst() { return static_cast<Model*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Model* getInst(Model_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Model>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Model_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Model* _o);
template <> inline PyObject* pyObject(chimera::Model const* _o) { return pyObject(const_cast<chimera::Model*>(_o)); }

} // namespace otf

#endif
