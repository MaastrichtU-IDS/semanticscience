#ifndef chimera_Link_object_h
# define chimera_Link_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "Mol.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Link_objectType;

struct Link_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	Link* _inst() { return static_cast<Link*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern Link* getInst(Link_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::Link>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Link_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::Link* _o);
template <> inline PyObject* pyObject(chimera::Link const* _o) { return pyObject(const_cast<chimera::Link*>(_o)); }

} // namespace otf

#endif
