#ifndef chimera_OpenModels_object_h
# define chimera_OpenModels_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "OpenModels.h"
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject OpenModels_objectType;

struct OpenModels_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	OpenModels* _inst() { return static_cast<OpenModels*>(_inst_data); }
	PyObject* _weaklist;
};

CHIMERA_IMEX extern OpenModels* getInst(OpenModels_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<chimera::OpenModels>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::OpenModels_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(chimera::OpenModels* _o);
template <> inline PyObject* pyObject(chimera::OpenModels const* _o) { return pyObject(const_cast<chimera::OpenModels*>(_o)); }

} // namespace otf

#endif
