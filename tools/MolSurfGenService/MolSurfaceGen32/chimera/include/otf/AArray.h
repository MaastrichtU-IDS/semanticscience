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

// $Id: AArray.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef otf_AArray_h
# define otf_AArray_h

# include "config.h"
# include "Array.h"
# include <iostream>
# include <stdexcept>
# include <math.h>

namespace otf {

// This header file provides a template class for fixed length arrays
// of an arithmetic type.

template <class T, size_t SIZE>
class AArray: public Array<T, SIZE>
{
	using Array<T, SIZE>::base;
public:
	typedef typename Array<T, SIZE>::size_type size_type;
	AArray() {}
	AArray(const T vec[SIZE])
	{
		for (size_type i = 0; i < SIZE; ++i)
			base[i] = vec[i];
	}

	// Since there are no pointers, memberwise copy is okay, and you
	// don't need an explicit copy constructor or operator=() function.

	bool operator==(const AArray& r) const
	{
		for (size_type i = 0; i < SIZE; ++i)
			if (base[i] != r.base[i])
				return 0;
		return 1;
	}

	bool operator!=(const AArray& r) const
	{
		for (size_type i = 0; i < SIZE; ++i)
			if (base[i] != r.base[i])
				return 1;
		return 0;
	}

	AArray operator+(const AArray& r) const
	{
		AArray	result;

		for (size_type i = 0; i < SIZE; ++i)
			result.base[i] = base[i] + r.base[i];
		return result;
	}

	void operator+=(const AArray& r)
	{
		for (size_type i = 0; i < SIZE; ++i)
			base[i] += r.base[i];
	}

	AArray operator-() const
	{
		AArray	result;

		for (size_type i = 0; i < SIZE; ++i)
			result.base[i] = - base[i];
		return result;
	}

	AArray operator-(const AArray& r) const
	{
		AArray	result;

		for (size_type i = 0; i < SIZE; ++i)
			result.base[i] = base[i] - r.base[i];
		return result;
	}

	void operator-=(const AArray& r)
	{
		for (size_type i = 0; i < SIZE; ++i)
			base[i] -= r.base[i];
	}

	AArray multiply(const AArray& r) const
	{
		AArray	result;

		for (size_type i = 0; i < SIZE; ++i)
			result.base[i] = base[i] * r.base[i];
		return result;
	}

	AArray divide(const AArray& r) const
	{
		AArray	result;

		for (size_type i = 0; i < SIZE; ++i)
			result.base[i] = base[i] / r.base[i];
		return result;
	}

	// dot product
	T operator*(const AArray& r) const
	{
		T	result = 0;

		for (size_type i = 0; i < SIZE; ++i)
			result += base[i] * r.base[i];
		return result;
	}

	AArray operator+(T f) const
	{
		AArray	result;

		for (size_type i = 0; i < SIZE; ++i)
			result.base[i] = base[i] + f;
		return result;
	}

	AArray operator-(T f) const
	{
		AArray	result;

		for (size_type i = 0; i < SIZE; ++i)
			result.base[i] = base[i] - f;
		return result;
	}

	AArray operator*(T f) const
	{
		AArray	result;

		for (size_type i = 0; i < SIZE; ++i)
			result.base[i] = base[i] * f;
		return result;
	}

	AArray operator/(T f) const
	{
		AArray	result;

		for (size_type i = 0; i < SIZE; ++i)
			result.base[i] = base[i] / f;
		return result;
	}

	void operator+=(T f)
	{
		for (size_type i = 0; i < SIZE; ++i)
			base[i] += f;
	}

	void operator-=(T f)
	{
		for (size_type i = 0; i < SIZE; ++i)
			base[i] -= f;
	}

	void operator*=(T f)
	{
		for (size_type i = 0; i < SIZE; ++i)
			base[i] *= f;
	}

	void operator/=(T f)
	{
		for (size_type i = 0; i < SIZE; ++i)
			base[i] /= f;
	}

	T sum() const
	{
		T	result = 0;

		for (size_type i = 0; i < SIZE; ++i)
			result += base[i];
		return result;
	}

	T sqlength() const
	{
		T	result = 0;

		for (size_type i = 0; i < SIZE; ++i)
			result += base[i] * base[i];
		return result;
	}

	double length() const
	{
		return sqrt(sqlength());
	}

	void negate()
	{
		for (size_type i = 0; i < SIZE; ++i)
			base[i] = - base[i];
	}

	void normalize()
	{
		double len = length();
		if (len == 0.0)
			throw std::domain_error("can't normalize zero length array");
		for (size_type i = 0; i < SIZE; ++i)
			base[i] /= len;
	}

	void setLength(T newlen)
	{
		T len = length();
		if (len <= 0.0)
			throw std::domain_error("length must be greater than zero");
		for (size_type i = 0; i < SIZE; ++i)
			base[i] *= newlen / len;
	}
};

template <>
class OTF_IMEX AArray<float, 3>: public Array<float, 3>
{
public:
	AArray() {}
	AArray(const float vec[3])
	{
		base[0] = vec[0]; base[1] = vec[1]; base[2] = vec[2];
	}

	// Since there are no pointers, memberwise copy is okay, and you
	// don't need an explicit copy constructor or operator=() function.

	bool operator==(const AArray& r) const
	{
		return base[0] == r.base[0] && base[1] == r.base[1] && base[2] == r.base[2];
	}

	bool operator!=(const AArray& r) const
	{
		return base[0] != r.base[0] || base[1] != r.base[1] || base[2] != r.base[2];
	}

	AArray operator+(const AArray& r) const
	{
		AArray	result;

		result.base[0] = base[0] + r.base[0];
		result.base[1] = base[1] + r.base[1];
		result.base[2] = base[2] + r.base[2];
		return result;
	}

	void operator+=(const AArray& r)
	{
		base[0] += r.base[0]; base[1] += r.base[1]; base[2] += r.base[2];
	}

	AArray operator-() const
	{
		AArray	result;

		result.base[0] = - base[0];
		result.base[1] = - base[1];
		result.base[2] = - base[2];
		return result;
	}

	AArray operator-(const AArray& r) const
	{
		AArray	result;

		result.base[0] = base[0] - r.base[0];
		result.base[1] = base[1] - r.base[1];
		result.base[2] = base[2] - r.base[2];
		return result;
	}

	void operator-=(const AArray& r)
	{
		base[0] -= r.base[0]; base[1] -= r.base[1]; base[2] -= r.base[2];
	}

	AArray multiply(const AArray& r) const
	{
		AArray	result;

		result.base[0] = base[0] * r.base[0];
		result.base[1] = base[1] * r.base[1];
		result.base[2] = base[2] * r.base[2];
		return result;
	}

	AArray divide(const AArray& r) const
	{
		AArray	result;

		result.base[0] = base[0] / r.base[0];
		result.base[1] = base[1] / r.base[1];
		result.base[2] = base[2] / r.base[2];
		return result;
	}

	// dot product
	float operator*(const AArray& r) const
	{
		return base[0] * r.base[0] + base[1] * r.base[1] + base[2] * r.base[2];
	}

	AArray operator+(float f) const
	{
		AArray	result;

		result.base[0] = base[0] + f;
		result.base[1] = base[1] + f;
		result.base[2] = base[2] + f;
		return result;
	}

	AArray operator-(float f) const
	{
		AArray	result;

		result.base[0] = base[0] - f;
		result.base[1] = base[1] - f;
		result.base[2] = base[2] - f;
		return result;
	}

	AArray operator*(float f) const
	{
		AArray	result;

		result.base[0] = base[0] * f;
		result.base[1] = base[1] * f;
		result.base[2] = base[2] * f;
		return result;
	}

	AArray operator/(float f) const
	{
		AArray	result;

		result.base[0] = base[0] / f;
		result.base[1] = base[1] / f;
		result.base[2] = base[2] / f;
		return result;
	}

	void operator+=(float f)
	{
		base[0] += f; base[1] += f; base[2] += f;
	}

	void operator-=(float f)
	{
		base[0] -= f; base[1] -= f; base[2] -= f;
	}

	void operator*=(float f)
	{
		base[0] *= f; base[1] *= f; base[2] *= f;
	}

	void operator/=(float f)
	{
		base[0] /= f; base[1] /= f; base[2] /= f;
	}

	float sum() const
	{
		return base[0] + base[1] + base[2];
	}

	float sqlength() const
	{
		return base[0] * base[0] + base[1] * base[1] + base[2] * base[2];
	}

	float length() const
	{
#ifndef OTF_NO_FLOAT_MATH_FUNCS
		return sqrtf(sqlength());
#else
		return sqrt(sqlength());
#endif
	}

	void negate()
	{
		base[0] = - base[0]; base[1] = - base[1]; base[2] = - base[2];
	}

	void normalize()
	{
		float len = length();
		if (len == 0.0)
			throw std::domain_error("can't normalize zero length array");
		base[0] /= len; base[1] /= len; base[2] /= len;
	}

	void setLength(float newlen)
	{
		float len = length();
		if (len <= 0.0)
			throw std::domain_error("length must be greater than zero");
		base[0] *= newlen / len;
		base[1] *= newlen / len;
		base[2] *= newlen / len;
	}
};

template <>
class OTF_IMEX AArray<double, 3>: public Array<double, 3>
{
public:
	AArray() {}
	AArray(const double vec[3])
	{
		base[0] = vec[0]; base[1] = vec[1]; base[2] = vec[2];
	}

	// Since there are no pointers, memberwise copy is okay, and you
	// don't need an explicit copy constructor or operator=() function.

	bool operator==(const AArray& r) const
	{
		return base[0] == r.base[0] && base[1] == r.base[1] && base[2] == r.base[2];
	}

	bool operator!=(const AArray& r) const
	{
		return base[0] != r.base[0] || base[1] != r.base[1] || base[2] != r.base[2];
	}

	AArray operator+(const AArray& r) const
	{
		AArray	result;

		result.base[0] = base[0] + r.base[0];
		result.base[1] = base[1] + r.base[1];
		result.base[2] = base[2] + r.base[2];
		return result;
	}

	void operator+=(const AArray& r)
	{
		base[0] += r.base[0]; base[1] += r.base[1]; base[2] += r.base[2];
	}

	AArray operator-() const
	{
		AArray	result;

		result.base[0] = - base[0];
		result.base[1] = - base[1];
		result.base[2] = - base[2];
		return result;
	}

	AArray operator-(const AArray& r) const
	{
		AArray	result;

		result.base[0] = base[0] - r.base[0];
		result.base[1] = base[1] - r.base[1];
		result.base[2] = base[2] - r.base[2];
		return result;
	}

	void operator-=(const AArray& r)
	{
		base[0] -= r.base[0]; base[1] -= r.base[1]; base[2] -= r.base[2];
	}

	AArray multiply(const AArray& r) const
	{
		AArray	result;

		result.base[0] = base[0] * r.base[0];
		result.base[1] = base[1] * r.base[1];
		result.base[2] = base[2] * r.base[2];
		return result;
	}

	AArray divide(const AArray& r) const
	{
		AArray	result;

		result.base[0] = base[0] / r.base[0];
		result.base[1] = base[1] / r.base[1];
		result.base[2] = base[2] / r.base[2];
		return result;
	}

	// dot product
	double operator*(const AArray& r) const
	{
		return base[0] * r.base[0] + base[1] * r.base[1] + base[2] * r.base[2];
	}

	AArray operator+(double f) const
	{
		AArray	result;

		result.base[0] = base[0] + f;
		result.base[1] = base[1] + f;
		result.base[2] = base[2] + f;
		return result;
	}

	AArray operator-(double f) const
	{
		AArray	result;

		result.base[0] = base[0] - f;
		result.base[1] = base[1] - f;
		result.base[2] = base[2] - f;
		return result;
	}

	AArray operator*(double f) const
	{
		AArray	result;

		result.base[0] = base[0] * f;
		result.base[1] = base[1] * f;
		result.base[2] = base[2] * f;
		return result;
	}

	AArray operator/(double f) const
	{
		AArray	result;

		result.base[0] = base[0] / f;
		result.base[1] = base[1] / f;
		result.base[2] = base[2] / f;
		return result;
	}

	void operator+=(double f)
	{
		base[0] += f; base[1] += f; base[2] += f;
	}

	void operator-=(double f)
	{
		base[0] -= f; base[1] -= f; base[2] -= f;
	}

	void operator*=(double f)
	{
		base[0] *= f; base[1] *= f; base[2] *= f;
	}

	void operator/=(double f)
	{
		base[0] /= f; base[1] /= f; base[2] /= f;
	}

	double sum() const
	{
		return base[0] + base[1] + base[2];
	}

	double sqlength() const
	{
		return base[0] * base[0] + base[1] * base[1] + base[2] * base[2];
	}

	double length() const
	{
		return sqrt(sqlength());
	}

	void negate()
	{
		base[0] = - base[0]; base[1] = - base[1]; base[2] = - base[2];
	}

	void normalize()
	{
		double len = length();
		if (len == 0.0)
			throw std::domain_error("can't normalize zero length array");
		base[0] /= len; base[1] /= len; base[2] /= len;
	}

	void setLength(double newlen)
	{
		double len = length();
		if (len <= 0.0)
			throw std::domain_error("length must be greater than zero");
		base[0] *= newlen / len;
		base[1] *= newlen / len;
		base[2] *= newlen / len;
	}
};

template <class T, size_t SIZE>
inline AArray<T, SIZE>
lerp(const AArray<T, SIZE>& l, const AArray<T, SIZE>& r, float alpha)
{
	AArray<T, SIZE>	result;

	for (typename AArray<T, SIZE>::size_type i = 0; i < SIZE; ++i)
		result[i] = l[i] + (r[i] - l[i]) * alpha;
	return result;
}

template <class T, size_t SIZE>
inline AArray<T, SIZE>
lerp(const AArray<T, SIZE>& l, const AArray<T, SIZE>& r, double alpha)
{
	AArray<T, SIZE>	result;

	for (typename AArray<T, SIZE>::size_type i = 0; i < SIZE; ++i)
		result[i] = l[i] + (r[i] - l[i]) * alpha;
	return result;
}

template <class T, size_t SIZE>
inline AArray<T, SIZE>
combine(const AArray<T, SIZE>& l, const AArray<T, SIZE>& r, float alpha, float beta)
{
	AArray<T, SIZE>	result;

	for (typename AArray<T, SIZE>::size_type i = 0; i < SIZE; ++i)
		result[i] = alpha * l[i] + beta * r[i];
	return result;
}

template <class T, size_t SIZE>
inline AArray<T, SIZE>
combine(const AArray<T, SIZE>& l, const AArray<T, SIZE>& r, double alpha, double beta)
{
	AArray<T, SIZE>	result;

	for (typename AArray<T, SIZE>::size_type i = 0; i < SIZE; ++i)
		result[i] = alpha * l[i] + beta * r[i];
	return result;
}

template <class T, size_t SIZE>
inline T
sqdistance(const AArray<T, SIZE>& l, const AArray<T, SIZE>& r)
{
	T sum = 0;
	for (typename AArray<T, SIZE>::size_type i = 0; i < SIZE; ++i) {
		T diff = l[i] - r[i];
		sum += diff * diff;
	}
	return sum;
}

template <class T, size_t SIZE>
inline double
distance(const AArray<T, SIZE>& l, const AArray<T, SIZE>& r)
{
	return sqrt(sqdistance(l, r));
}

#ifndef _WIN32
inline float
#else
inline double
#endif
distance(const AArray<float, 3>& l, const AArray<float, 3>& r)
{
#ifndef OTF_NO_FLOAT_MATH_FUNCS
	return sqrtf(sqdistance(l, r));
#else
	return sqrt(sqdistance(l, r));
#endif
}

template <class T>
inline AArray<T, 3>
cross(const AArray<T, 3>& l, const AArray<T, 3>& r)
{
	AArray<T, 3>	result;

	result[0] = (l[1] * r[2]) - (l[2] * r[1]);
	result[1] = (l[2] * r[0]) - (l[0] * r[2]);
	result[2] = (l[0] * r[1]) - (l[1] * r[0]);
	return result;
}

template <class T, size_t SIZE>
inline AArray<T, SIZE>
operator+(T f, const AArray<T, SIZE>& r)
{
	return r.operator+(f);
}

template <class T, size_t SIZE>
inline AArray<T, SIZE>
operator*(T f, const AArray<T, SIZE>& r)
{
	return r.operator*(f);
}

template <class T, size_t SIZE>
inline std::ostream&
operator<<(std::ostream& os, const AArray<T, SIZE>& r)
{
	os << r[0];
	for (typename AArray<T, SIZE>::size_type i = 1; i < SIZE; ++i)
		os << ' ' << r[i];
	return os;
}

} // namespace otf

#endif
