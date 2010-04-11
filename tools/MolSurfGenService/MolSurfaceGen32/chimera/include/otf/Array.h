// Copyright (c) 1996 The Regents of the University of California.
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

// $Id: Array.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef otf_Array_h
# define otf_Array_h

# include "config.h"
# include <iostream>
# include <iterator>
# include <stdexcept>
# include <stddef.h>

# if defined(__MWERKS__) && ! defined(__APPLE__)
// don't understand yet why this is needed
using std::size_t;
using std::ptrdiff_t;
# endif

namespace otf {

template <class T, size_t SIZE>
class Array {
protected:
	T base[SIZE];
public:
	typedef T value_type;
	typedef value_type *iterator;
	typedef value_type const *const_iterator;
	typedef value_type& reference;
	typedef value_type const& const_reference;
	typedef size_t size_type;
	typedef ptrdiff_t difference_type;
#ifndef OTF_NO_CLASS_PARTIAL_SPECIALIZATION
	typedef std::reverse_iterator<const_iterator> const_reverse_iterator;
	typedef std::reverse_iterator<iterator> reverse_iterator;
#else
	typedef std::reverse_iterator<const_iterator, value_type,
		const_reference, difference_type> const_reverse_iterator;
	typedef std::reverse_iterator<iterator, value_type, reference,
					difference_type> reverse_iterator;
#endif

	iterator begin() { return &base[0]; }
	iterator end() { return &base[SIZE]; }
	const_iterator begin() const { return &base[0]; }
	const_iterator end() const { return &base[SIZE]; }
	reverse_iterator rbegin() { return reverse_iterator(end()); }
	reverse_iterator rend() { return reverse_iterator(begin()); }
	const_reverse_iterator rbegin() const { return const_reverse_iterator(end()); }
	const_reverse_iterator rend() const { return const_reverse_iterator(begin()); }

	static size_type max_size() { return SIZE; }
	static size_type size() { return SIZE; }
	reference operator[](size_type i) { return base[i]; }
	const_reference operator[](size_type i) const { return base[i]; }
	reference at(size_type i)
#if defined(__DECCXX_VER) && __DECCXX_VER < 60590032
		;
#else
	{
		if (i >= SIZE)
			throw std::out_of_range("index out of range");
		return base[i];
	}
#endif
	const_reference at(size_type i) const
#if defined(__DECCXX_VER) && __DECCXX_VER < 60590032
		;
#else
	{
		if (i >= SIZE)
			throw std::out_of_range("index out of range");
		return base[i];
	}
#endif
};

template <class T, size_t SIZE>
inline static std::ostream&
operator<<(std::ostream& os, const Array<T, SIZE>& r)
{
	os << r[0];
	for (typename Array<T, SIZE>::size_type i = 1; i < SIZE; ++i)
		os << ' ' << r[i];
	return os;
}

#if defined(__DECCXX_VER) && __DECCXX_VER < 60590032
// workaround -- declare specializations so they're not inlined!

template <class T, size_t SIZE>
typename Array<T, SIZE>::reference
Array<T, SIZE>::at(Array<T, SIZE>::size_type i)
{
	if (i >= SIZE)
		throw std::out_of_range("index out of range");
	return base[i];
}

template <class T, size_t SIZE>
typename Array<T, SIZE>::const_reference
Array<T, SIZE>::at(Array<T, SIZE>::size_type i) const
{
	if (i >= SIZE)
		throw std::out_of_range("index out of range");
	return base[i];
}

template <> double &Array<double, 3>::at(size_t);
template <> const double &Array<double, 3>::at(size_t) const;

#endif

} // namespace otf

#endif
