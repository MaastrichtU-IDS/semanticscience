#ifndef _PythonModel__PythonModel_object_h
# define _PythonModel__PythonModel_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include "PM.h"
#include <otf/WrapPy2.h>
namespace _PythonModel {

extern PyTypeObject _PythonModel_objectType;

struct _PythonModel_object: public PyObject {
	PyObject* _inst_dict;
	otf::WrapPyObj* _inst_data;
	_PythonModel* _inst() { return static_cast<_PythonModel*>(_inst_data); }
	PyObject* _weaklist;
};

extern _PythonModel* getInst(_PythonModel_object* self);

} // namespace _PythonModel

namespace otf {

template <> inline bool
WrapPyType<_PythonModel::_PythonModel>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &_PythonModel::_PythonModel_objectType);
}

template <> PyObject* pyObject(_PythonModel::_PythonModel* _o);
template <> inline PyObject* pyObject(_PythonModel::_PythonModel const* _o) { return pyObject(const_cast<_PythonModel::_PythonModel*>(_o)); }

} // namespace otf

#endif
