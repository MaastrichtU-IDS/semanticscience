#ifndef chimera_Element_object_h
# define chimera_Element_object_h
# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# define PY_SSIZE_T_CLEAN 1
#include <Python.h>
# include <otf/molkit/Element.h>
#include <otf/WrapPy2.h>
namespace chimera {

CHIMERA_IMEX extern PyTypeObject Element_objectType;

struct Element_object: public PyObject {
	PyObject* _inst_dict;
	double _inst_data[(sizeof (otf::Element) + sizeof (double) - 1) / sizeof (double)];
	bool _initialized;
	otf::Element* _inst() { return reinterpret_cast<otf::Element*>(_inst_data); }
};

CHIMERA_IMEX extern otf::Element* getInst(Element_object* self);

} // namespace chimera

namespace otf {

template <> inline bool
WrapPyType<otf::Element>::check(PyObject* _o, bool noneOk)
{
	if (noneOk && _o == Py_None)
		return true;
	return PyObject_TypeCheck(_o, &chimera::Element_objectType);
}

template <> CHIMERA_IMEX PyObject* pyObject(otf::Element* _o);
template <> inline PyObject* pyObject(otf::Element _o) { return pyObject(&_o); }
template <> inline PyObject* pyObject(otf::Element const* _o) { return pyObject(const_cast<otf::Element*>(_o)); }

} // namespace otf

#endif
