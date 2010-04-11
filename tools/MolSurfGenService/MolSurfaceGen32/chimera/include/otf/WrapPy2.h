// Copyright (c) 1998-2000 The Regents of the University of California.
// All rights reserved.
//
// Redistribution and use in source and binary forms are permitted
// provided that the above copyright notice and this paragraph are
// duplicated in all such forms and that any documentation,
// distribution and/or use acknowledge that the software was developed
// by the Computer Graphics Laboratory, University of California,
// San Francisco.  The name of the University may not be used to
// endorse or promote products derived from this software without
// specific prior written permission.
// 
// THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
// WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
// IN NO EVENT SHALL THE REGENTS OF THE UNIVERSITY OF CALIFORNIA BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
// OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF THIS SOFTWARE.

// $Id: WrapPy2.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef otf_WrapPy_h
# define otf_WrapPy_h

# ifndef OTF_WRAPPY_DLL
#  define OTF_WRAPPY_IMEX
# elif defined(OTF_WRAPPY_EXPORT)
#  define OTF_WRAPPY_IMEX __declspec(dllexport)
# else
#  define OTF_WRAPPY_IMEX __declspec(dllimport)
# endif

// see wrappy's documentation for more details
//
// _WC is the wrapped C++ class
//
// A wrapped C++ class, _WC, has an additional base class, WrapPyObj.
// The wpyGetObject() member function is used to return an owned Python object.
//
// Use WrapPyType<_WC>::check(PyObject*) to check if the PyObject is
// of the wrapped type (typically WC_objectType).
//

# define PY_SSIZE_T_CLEAN 1
# include <Python.h>
#if PY_VERSION_HEX < 0x02050000 && !defined(PY_SSIZE_T_MIN)
typedef int Py_ssize_t;
#define PY_SSIZE_T_MAX INT_MAX
#define PY_SSIZE_T_MIN INT_MIN
#endif
# include <stdexcept>
# include <string>
# include <vector>
# include <list>
# include <set>
# include <map>
# include <iostream>
# include "WrapPyFile.h"

namespace otf {

// like PyNumber_Check, but only check if convertible to int or float, not both
extern OTF_WRAPPY_IMEX bool WrapPyInt_Check(PyObject* obj);
extern OTF_WRAPPY_IMEX bool WrapPyFloat_Check(PyObject* obj);
extern OTF_WRAPPY_IMEX bool WrapPyLong_Check(PyObject* obj);

class PythonError: public std::runtime_error
{
	// Throw a PythonError in wrapped functions when a Python error
	// has occurred, so the Python error will propagate back.
public:
	PythonError(): std::runtime_error("Python Error") {}
};

// forward declarations for templates
template <class _c> PyObject* pyObject(_c _x);
template <class _iterator> PyObject* cvtSequenceToPyList(_iterator _b, _iterator _e);
template <class _iterator> PyObject* cvtSequenceToPyTuple(_iterator _b, _iterator _e);
template <class _iterator> PyObject* cvtSetToPySet(_iterator _b, _iterator _e);
template <class _iterator> PyObject* cvtMapToPyDict(_iterator _b, _iterator _e);
template <class _MultiMap> PyObject* cvtMultiMapToPyDict(_MultiMap const& _mm);
template <class _iterator> PyObject* cvtMultiMapToPyDict(_iterator _b, _iterator _e);

template <class _WC>
struct WrapPyType
{
	static bool check(PyObject*, bool noneOk = false);
};

enum WrapPyCreate { PWC_DONT_CREATE, PWC_CREATE, PWC_CREATE_AND_OWN };

class OTF_WRAPPY_IMEX WrapPyObj
{
	// use as a non-template base class, so we can dynamic_cast to/from it
	void operator=(const WrapPyObj&);
protected:
	mutable PyObject* pyObj;
	mutable bool owner;	// true if Python dealloc deletes C++ object
public:
	WrapPyObj(): pyObj(0), owner(false) {}
	WrapPyObj(const WrapPyObj&): pyObj(0), owner(false) {}
	PyObject* wpyGetObject(WrapPyCreate pwc = PWC_CREATE) const;
	virtual PyObject* wpyNew() const = 0;
	virtual void wpyDisassociate();	// for Python Object's dealloc method
	virtual void wpyAssociate(PyObject* o) const;
	bool pyOwned() const { return owner; }
	void setPyOwned() { owner = true; }
	virtual ~WrapPyObj();
};

extern "C" {

// All Python types for subclasses of WrapPyObj
// must have the exact layout as WrapPyObj_object.
struct WrapPyObj_object: public PyObject
{
	PyObject*	_inst_dict;
	WrapPyObj*	_inst_data;
	PyObject*	_weaklist;
};

OTF_WRAPPY_IMEX extern PyTypeObject WrapPyObj_objectType;
OTF_WRAPPY_IMEX extern PyTypeObject WrapPyMutable_Type;

} // extern "C"

//
// The pyObject template is for converting C++ types to Python types
//

# ifdef TODO
// Can't specialize function templates yet
template <class _c> PyObject*
pyObject<_c*>(_c* xp)
{
	if (xp == NULL) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	return xp->wpyGetObject();
}
# endif

template <> inline PyObject*
pyObject(char _x) { return PyString_FromStringAndSize(&_x, int(_x != '\0')); }

template <> inline PyObject*
pyObject(bool _x)
{	
	PyObject* _o = (_x) ? Py_True : Py_False;
	Py_INCREF(_o);
	return _o;
}

// TODO: figure out how to give optional allocator to std::vector<bool>
template <> inline PyObject*
pyObject(std::vector<bool>::reference _x)
{
	return PyInt_FromLong(static_cast<long>(_x));
}

template <> inline PyObject*
pyObject(short _x) { return PyInt_FromLong(static_cast<long>(_x)); }

template <> inline PyObject*
pyObject(int _x) { return PyInt_FromLong(static_cast<long>(_x)); }

template <> inline PyObject*
pyObject(long _x) { return PyInt_FromLong(_x); }

template <> inline PyObject*
pyObject(unsigned long _x) { return PyLong_FromUnsignedLong(_x); }

# ifdef HAVE_LONG_LONG
template <> inline PyObject*
pyObject(long long _x) { return PyLong_FromLongLong(_x); }

template <> inline PyObject*
pyObject(unsigned long long _x) { return PyLong_FromUnsignedLongLong(_x); }
# endif

template <> inline PyObject*
pyObject(float _x) { return PyFloat_FromDouble(static_cast<double>(_x)); }

template <> inline PyObject*
pyObject(double _x) { return PyFloat_FromDouble(_x); }

template <> inline PyObject*
pyObject(char const* _x)
{
	if (_x == NULL) {
		Py_INCREF(Py_None);
		return Py_None;
	}
	return PyString_FromString(_x);
}

template <> inline PyObject*
pyObject(std::string _x) { return PyString_FromStringAndSize(_x.data(), _x.size()); }

template <> inline PyObject*
pyObject(const std::string &_x) { return PyString_FromStringAndSize(_x.data(), _x.size()); }

template <> inline PyObject*
pyObject(PyObject* _x) { Py_XINCREF(_x); return _x; }

# if 0
// leave undefined so we get compiler/linkage errors
template <> inline PyObject*
pyObject(std::istream* _x) { throw std::runtime_error("wrong way"); }

template <> inline PyObject*
pyObject(std::ostream* _x) { throw std::runtime_error("wrong way"); }
# endif

template <class _c> PyObject*
pyObject(std::vector<_c> const& container)
{
	return cvtSequenceToPyList(container.begin(), container.end());
}

template <class _c> PyObject*
pyObject(std::list<_c> const& container)
{
	return cvtSequenceToPyList(container.begin(), container.end());
}

template <class _c> PyObject*
pyObject(std::set<_c> const& container)
{
	return cvtSetToPySet(container.begin(), container.end());
}

template <class _c> PyObject*
pyObject(std::multiset<_c> const& container)
{
	return cvtSequenceToPyList(container.begin(), container.end());
}

template <class _c, class _d> PyObject*
pyObject(std::map<_c, _d> const& container)
{
	return cvtMapToPyDict(container.begin(), container.end());
}

template <class _c, class _d> PyObject*
pyObject(std::multimap<_c, _d> const& container)
{
	return cvtMultiMapToPyDict(container);
}

template <class _c, class _d> PyObject*
pyObject(std::pair<_c, _d> const& _p)
{
	PyObject* _r = PyTuple_New(2);
	PyObject* _fo = pyObject(_p.first);
	if (_fo == NULL) {
		Py_DECREF(_r);
		return NULL;
	}
	PyTuple_SET_ITEM(_r, 0, _fo);
	PyObject* _so = pyObject(_p.second);
	if (_so == NULL) {
		Py_DECREF(_r);
		return NULL;
	}
	PyTuple_SET_ITEM(_r, 1, _so);
	return _r;
}

// nomenclature:
//
//	_r	result
//	_b	beginning of range
//	_e	end of range
//	_i	integer index
//	_n	next item in range
//	_k	key
//	_ko	key object
//	_vo	value object

template <class _iterator> PyObject*
cvtSequenceToPyList(_iterator _b, _iterator _e)
{
	PyObject* _r = PyList_New(std::distance(_b, _e));
	if (_r == NULL)
		return NULL;
	for (Py_ssize_t _i = 0; _b != _e; ++_i, ++_b) {
# ifndef OTF_NEED_EXPLICIT_TEMPLATES
		PyObject* _vo = pyObject(*_b);
# else
		PyObject* _vo = pyObject<std::iterator_traits<_iterator>::value_type>(*_b);
# endif
		if (_vo == NULL) {
			Py_DECREF(_r);
			return NULL;
		}
# ifdef PyList_SET_ITEM
		PyList_SET_ITEM(_r, _i, _vo);
# else
		PyList_SetItem(_r, _i, _vo);
# endif
	}
	return _r;
}

template <class _iterator> PyObject*
cvtSequenceToPyTuple(_iterator _b, _iterator _e)
{
	PyObject* _r = PyTuple_New(std::distance(_b, _e));
	if (_r == NULL)
		return NULL;
	for (Py_ssize_t _i = 0; _b != _e; ++_i, ++_b) {
# ifndef OTF_NEED_EXPLICIT_TEMPLATES
		PyObject* _vo = pyObject(*_b);
# else
		PyObject* _vo = pyObject<std::iterator_traits<_iterator>::value_type>(*_b);
# endif
		if (_vo == NULL) {
			Py_DECREF(_r);
			return NULL;
		}
# ifdef PyTuple_SET_ITEM
		PyTuple_SET_ITEM(_r, _i, _vo);
# else
		PyTuple_SetItem(_r, _i, _vo);
# endif
	}
	return _r;
}

# ifdef OTF_NEED_EXPLICIT_TEMPLATES
template <class _t>
struct StripConst
{
	typedef _t type;
	typedef _t const const_type;
};
# endif

inline Py_complex
makePy_complex(double r, double i)
{
	Py_complex c;
	c.real = r;
	c.imag = i;
	return c;
}

template <class _iterator> PyObject*
cvtSetToPySet(_iterator _b, _iterator _e)
{
# if PY_VERSION_HEX < 0x02050000
	// This follows internal Python/Objects/setobject.c code because
	// there is no external API.
	PySetObject* _so = reinterpret_cast<PySetObject*>(
				PySet_Type.tp_new(&PySet_Type, NULL, NULL));
	if (_so == NULL)
		return NULL;
	PyObject* _data = _so->data;	// borrowed reference
	for (; _b != _e; ++_b) {
#  ifndef OTF_NEED_EXPLICIT_TEMPLATES
		PyObject* _vo = pyObject(*_b);
#  else
		PyObject* _vo = pyObject<std::iterator_traits<_iterator>::value_type::second_type>(*_b);
#  endif
		if (_vo == NULL || PyDict_SetItem(_data, _vo, Py_True) == -1) {
			Py_XDECREF(_vo);
			Py_DECREF(_so);
			return NULL;
		}
		Py_DECREF(_vo);
	}
	return reinterpret_cast<PyObject*>(_so);
# else
	PyObject* _tmp = cvtSequenceToPyList(_b, _e);
	if (_tmp == NULL)
		return NULL;
	PyObject* _r = PySet_New(_tmp);
	Py_DECREF(_tmp);
	return _r;
# endif
}

template <class _iterator> PyObject*
cvtMapToPyDict(_iterator _b, _iterator _e)
{
	PyObject* _r = PyDict_New();
	if (_r == NULL)
		return NULL;
	for (; _b != _e; ++_b) {
# ifndef OTF_NEED_EXPLICIT_TEMPLATES
		PyObject* _ko = pyObject(_b->first);
# else
		PyObject* _ko = pyObject<StripConst<std::iterator_traits<_iterator>::value_type::first_type>::type>(_b->first);
# endif
		if (_ko == NULL) {
			Py_DECREF(_r);
			return NULL;
		}
# ifndef OTF_NEED_EXPLICIT_TEMPLATES
		PyObject* _vo = pyObject(_b->second);
# else
		PyObject* _vo = pyObject<std::iterator_traits<_iterator>::value_type::second_type>(_b->second);
# endif
		if (_vo == NULL) {
			Py_DECREF(_ko);
			Py_DECREF(_r);
			return NULL;
		}
		int _i = PyDict_SetItem(_r, _ko, _vo);
		Py_DECREF(_ko);
		Py_DECREF(_vo);
		if (_i == -1) {
			Py_DECREF(_r);
			return NULL;
		}
	}
	return _r;
}

template <class _MultiMap> PyObject*
cvtMultiMapToPyDict(_MultiMap const& _mm)
{
	PyObject* _r = PyDict_New();
	if (_r == NULL)
		return NULL;
	for (typename _MultiMap::const_iterator _b = _mm.begin(); _b != _mm.end();) {
		typename _MultiMap::key_type const _k = _b->first;
		typename _MultiMap::const_iterator _n = _mm.upper_bound(_k);
		PyObject* _vo = PyList_New(std::distance(_b, _n));
		if (_vo == NULL) {
			Py_DECREF(_r);
			return NULL;
		}
		for (Py_ssize_t _i = 0; _b != _n; ++_i, ++_b) {
# ifndef OTF_NEED_EXPLICIT_TEMPLATES
			PyObject* _o = pyObject(_b->second);
# else
			PyObject* _o = pyObject<_MultiMap::mapped_type>(_b->second);
# endif
			if (_o == NULL) {
				Py_DECREF(_vo);
				Py_DECREF(_r);
				return NULL;
			}
# ifdef PyList_SET_ITEM
			PyList_SET_ITEM(_vo, _i, _o);
# else
			PyList_SetItem(_vo, _i, _o);
# endif
		}
# ifndef OTF_NEED_EXPLICIT_TEMPLATES
		PyObject* _ko = pyObject(_k);
# else
		PyObject* _ko = pyObject<_MultiMap::key_type>(_k);
# endif
		if (_ko == NULL) {
			Py_DECREF(_vo);
			Py_DECREF(_r);
			return NULL;
		}
		PyDict_SetItem(_r, _ko, _vo);
		Py_DECREF(_ko);
		Py_DECREF(_vo);
	}
	return _r;
}

template <class _iterator> PyObject*
cvtMultiMapToPyDict(_iterator _b, _iterator _e)
{
	PyObject* _r = PyDict_New();
	if (_r == NULL)
		return NULL;
	_iterator _n;
	for (; _b != _e; _b = _n) {
		PyObject* _vo = PyList_New(0);
		if (_vo == NULL) {
			Py_DECREF(_r);
			return NULL;
		}
		for (_n = _b; _n != _e && _n->first == _b->first; ++_n) {
# ifndef OTF_NEED_EXPLICIT_TEMPLATES
			PyObject* _o = pyObject(_n->second);
# else
			PyObject* _o = pyObject<std::iterator_traits<_iterator>::value_type::second_type>(_n->second);
# endif
			if (_o == NULL) {
				Py_DECREF(_vo);
				Py_DECREF(_r);
				return NULL;
			}
			PyList_Append(_vo, _o);
			Py_DECREF(_o);
		}
# ifndef OTF_NEED_EXPLICIT_TEMPLATES
		PyObject* _ko = pyObject(_b->first);
# else
		PyObject* _ko = pyObject<StripConst<std::iterator_traits<_iterator>::value_type::first_type>::type>(_b->first);
# endif
		if (_ko == NULL) {
			Py_DECREF(_r);
			return NULL;
		}
		PyDict_SetItem(_r, _ko, _vo);
		Py_DECREF(_ko);
		Py_DECREF(_vo);
	}
	return _r;
}

extern OTF_WRAPPY_IMEX int WrapPyMutableType_Ready(PyTypeObject* t);

// for module building (ideally this code would be part of Python)
extern OTF_WRAPPY_IMEX int PyType_AddObject(PyTypeObject* t, const char* name,
								PyObject* o);

extern OTF_WRAPPY_IMEX std::string PyBaseString_AsCppString(PyObject *obj);

} // namespace otf

// Python module init function
extern "C" OTF_WRAPPY_IMEX void initlibwrappy2();

#endif
