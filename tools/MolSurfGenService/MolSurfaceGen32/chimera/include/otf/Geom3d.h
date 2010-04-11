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

// $Id: Geom3d.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef otf_Geom3d_h
# define otf_Geom3d_h

//# include <otf/config.h>
# include "AArray.h"

namespace otf {

namespace Geom3d {

// Note: all angles are in degrees.

typedef double Real;
typedef AArray<Real, 3> _3tuple;

class Point;
class Vector;
class BBox;
class Xform;

inline bool
fuzzyEqual(float f, float g)
{
	const float EPSILON = 1.0e-5f;
	if (f <= g)
		return f >= g - EPSILON;
	else
		return f <= g + EPSILON;
}

inline bool
fuzzyEqual(double f, double g)
{
	const double EPSILON = 1.0e-10;
	if (f <= g)
		return f >= g - EPSILON;
	else
		return f <= g + EPSILON;
}

class OTF_IMEX Point {
	_3tuple data_;
	friend class Vector;
	friend class PointAdd;
	friend inline std::ostream& operator<<(std::ostream&, const Point&); 
public:
	typedef _3tuple::size_type size_type;	// size_t
	Point() { data_[0] = data_[1] = data_[2] = 0; }
	Point(Real x, Real y, Real z) { data_[0] = x; data_[1] = y; data_[2] = z; }
	explicit Point(const Real p[3]): data_(p) {}
	explicit Point(const _3tuple& p): data_(p) {}
	// The following two templates construct a Point from a weighted
	// set of other Points.
	template <class pointIterator>
		Point(pointIterator ptStart, pointIterator ptStop);
	template <class pointIterator, class coefIterator>
		Point(pointIterator ptStart, pointIterator ptStop,
				coefIterator coefStart, coefIterator coefStop);
	Real	x() const { return data_[0]; }
	Real	y() const { return data_[1]; }
	Real	z() const { return data_[2]; }
	void	setX(Real x) { data_[0] = x; }
	void	setY(Real y) { data_[1] = y; }
	void	setZ(Real z) { data_[2] = z; }
	const AArray<Real, 3>& data() const { return data_; }

	// only enable AArray functions that make sense for Points
	bool	operator==(const Point& r) const {
			return data_ == r.data_;
		}
	bool	operator!=(const Point& r) const {
			return data_ != r.data_;
		}

	typedef _3tuple::reference reference;
	reference operator[](size_type i) { return data_[i]; }
	reference at(size_type i) { return data_.at(i); }
	typedef _3tuple::const_reference const_reference;
	const_reference operator[](size_type i) const { return data_[i]; }
	const_reference at(size_type i) const { return data_.at(i); }
	static size_type size() { return _3tuple::size(); }

	Vector	operator-(const Point& r) const;
	Vector	toVector() const;
	Point	operator+(const Vector& r) const;
	void	operator+=(const Vector& r);
	Point	operator-(const Vector& r) const;
	void	operator-=(const Vector& r);
	Real	distance(const Point& r) const;
	Real	sqdistance(const Point& r) const;
};

template <class pointIterator>
Point::Point(pointIterator ptStart, pointIterator ptStop)
{
	if (ptStart == ptStop)
		throw std::runtime_error("empty list of points");

	const Point& pt = *ptStart;
	_3tuple accum = pt.data_;
	int totalWeight = 1;
	for (++ptStart; ptStart != ptStop; ++ptStart) {
		const Point& pt = *ptStart;
		accum += pt.data_;
		++totalWeight;
	}
	data_ = accum / totalWeight;
}

template <class pointIterator, class coefIterator>
Point::Point(pointIterator ptStart, pointIterator ptStop, coefIterator coefStart, coefIterator coefStop)
{
	if (ptStart == ptStop)
		throw std::runtime_error("empty list of points");
	if (coefStart == coefStop)
		throw std::runtime_error("empty list of coefficients");

	const Point& pt = *ptStart;
	Real totalWeight = *coefStart;
	_3tuple accum = totalWeight * pt.data_;
	for (++ptStart, ++coefStart; ptStart != ptStop && coefStart != coefStop;
						++ptStart, ++coefStart) {
		const Point& pt = *ptStart;
		Real coef = *coefStart;
		accum += coef * pt.data_;
		totalWeight += coef;
	}
	if (ptStart != ptStop)
		throw std::runtime_error("not enough coeffients");
	if (coefStart != coefStop)
		throw std::runtime_error("not enough points");
	data_ = accum / totalWeight;
}

// PointAdd: provide a type-safe way to add Points (i.e., returned a
// weighted average of points).

class OTF_IMEX PointAdd {
	Real	totalWeight_;
	_3tuple	accum;
public:
	PointAdd();
	PointAdd(const Point& p, Real weight = 1);
	void	reset();
	void	add(const Point& p, Real weight = 1);
	Real	totalWeight() const;
	Point	point() const;
};

inline
PointAdd::PointAdd()
{
	totalWeight_ = 0;
	accum[0] = accum[1] = accum[2] = 0;
}

inline
PointAdd::PointAdd(const Point& p, Real weight)
{
	totalWeight_ = weight;
	accum = p.data_;
}

inline void
PointAdd::reset()
{
	totalWeight_ = 0;
	accum[0] = accum[1] = accum[2] = 0;
}

inline void
PointAdd::add(const Point& p, Real weight)
{
	totalWeight_ += weight;
	accum += p.data_ * weight;
}

inline Real
PointAdd::totalWeight() const
{
	return totalWeight_;
}

inline Point
PointAdd::point() const
{
	if (totalWeight_ == 0)
		return Point();
	else
		return Point(accum / totalWeight_);
}

class OTF_IMEX Vector {
	_3tuple data_;
	friend class Point;
	friend inline std::ostream& operator<<(std::ostream&, const Vector&); 
public:
	typedef _3tuple::size_type size_type;
	Vector() { data_[0] = data_[1] = data_[2] = 0; }
	Vector(Real x, Real y, Real z) { data_[0] = x; data_[1] = y; data_[2] = z;}
	explicit Vector(const Real v[3]): data_(v) {}
	explicit Vector(const _3tuple& v): data_(v) {}
	Real	x() const { return data_[0]; }
	Real	y() const { return data_[1]; }
	Real	z() const { return data_[2]; }
	void	setX(Real x) { data_[0] = x; }
	void	setY(Real y) { data_[1] = y; }
	void	setZ(Real z) { data_[2] = z; }
	const AArray<Real, 3>& data() const { return data_; }

	// only enable AArray functions that make sense for Vectors
	bool	operator==(const Vector& r) const {
			return data_ == r.data_;
		}
	bool	operator!=(const Vector& r) const {
			return data_ != r.data_;
		}

	typedef _3tuple::reference reference;
	reference operator[](size_type i) { return data_[i]; }
	reference at(size_type i) { return data_.at(i); }
	typedef _3tuple::const_reference const_reference;
	const_reference operator[](size_type i) const { return data_[i]; }
	const_reference at(size_type i) const { return data_.at(i); }
	static size_type size() { return _3tuple::size(); }

	Vector	operator+(const Vector& r) const {
			return Vector(data_ + r.data_);
		}
	void	operator+=(const Vector& r) {
			data_ += r.data_;
		}
	Vector	operator-() const {
			return Vector(-data_);
		}
	Vector	operator-(const Vector& r) const {
			return Vector(data_ - r.data_);
		}
	void	operator-=(const Vector& r) {
			data_ -= r.data_;
		}
	Real	operator*(const Vector& r) const {
			return data_ * r.data_;
		}
	Vector	operator*(Real f) const {
			return Vector(data_ * f);
		}
	Vector	operator/(Real f) const {
			return Vector(data_ / f);
		}
	void	operator*=(Real f) {
			data_ *= f;
		}
	void	operator/=(Real f) {
			data_ /= f;
		}
	Real	sqlength() const {
			return data_.sqlength();
		}
	double	length() const {
			return data_.length();
		}
	void	normalize() {
			data_.normalize();
		}
	void	setLength(Real newlen) {
			data_.setLength(newlen);
		}
	void	negate() {
			data_.negate();
		}
	Point	operator+(const Point& r) const {
			return Point(data_ + r.data_);
		}
};

inline Vector
operator*(Real f, const Vector& v)
{
	Vector r(v);
	r *= f;
	return r;
}

// BBox: currently an axis-aligned Bounding-Box, should probably switch
// to an oriented Bounding-Box.

class OTF_IMEX BBox {
public:
	Point	llf;	// lower-left-front
	Point	urb;	// upper-right-back
	void	merge(const BBox& b);
	void	xform(const Xform& xf);
	bool	inside(const Point& xyz) const;
	void	add(const Point& xyz);
	Point	center() const;
};

//	Xform holds a orthonormal rotation 3x3 matrix and a translation
//	vector (so no scaling, no shear, no projection).  Consequently,
//	we never have to renormalize normals.

class OTF_IMEX Xform {
private:
	friend inline std::ostream&
				operator<<(std::ostream& os, const Xform& t);
	Real	rot[3][3];
	Vector	xlate, inv_xlate;
	bool	isIdentity_;
		Xform(bool ident);
		Xform(const Real m[3][3], const Real t[3], const Real it[3],
							bool ident = false);
	friend class BBox;
public:
	Xform();		// same as identity
	static Xform	xform(Real r00, Real r01, Real r02, Real t03,
				Real r10, Real r11, Real r12, Real t13,
				Real r20, Real r21, Real r22, Real t23,
				bool orthogonalize = false);
	static Xform	coordFrame(const Vector& x, const Vector& y,
				const Vector& z, const Point& origin,
				bool orthogonalize = false);
	static Xform	identity();
	static Xform	translation(Real x, Real y, Real z);
	static Xform	translation(const Vector& xyz);
	static Xform	xRotation(Real angle);
	static Xform	yRotation(Real angle);
	static Xform	zRotation(Real angle);
	static Xform	rotation(Real x, Real y, Real z, Real angle);
	static Xform	rotation(const Vector& xyz, Real angle);
	static Xform	rotation(const Real mat[3][3],
						bool orthogonalize = false);
	static Xform	zAlign(const Point& p0, const Point& p1);
	static Xform	zAlign(const Point& p, const Vector& v);
	static Xform	lookAt(const Point& eye, const Point& at,
							const Point& up);
	static Xform	lookAt(const Point& eye, const Point& at,
							const Vector& up);
	void	invert();
	Xform	inverse() const;
	void	translate(Real x, Real y, Real z);
	void	translate(const Vector& xyz);
	void	xRotate(Real angle);
	void	yRotate(Real angle);
	void	zRotate(Real angle);
	void	rotate(Real x, Real y, Real z, Real angle);
	void	rotate(const Vector& xyz, Real angle);
	Point	apply(const Point& p) const;
	Vector	apply(const Vector& p) const;
	void	premultiply(const Xform& op);
	void	multiply(const Xform& op);
	bool	isIdentity() const;
	void	getRotation(Vector *axis, Real *angle) const;
	void	getTranslation(Real *x, Real *y, Real *z) const;
	void	getTranslation(/*OUT*/ Vector *v) const;
	void	getCoordFrame(/*OUT*/ Vector *x = NULL,
			/*OUT*/ Vector *y = NULL, /*OUT*/ Vector *z = NULL,
			/*OUT*/ Point *origin = NULL) const;
	void	getOpenGLMatrix(Real mat[16]) const;
	void	makeOrthogonal(bool modify);
};

OTF_IMEX Real	dihedral(const Point& p0, const Point& p1, const Point& p2,
							const Point& p3);
OTF_IMEX Real	angle(const Vector& v0, const Vector& v1);
OTF_IMEX Real	angle(const Point& p0, const Point& p1, const Point& p2);

inline float degrees(float radians) { return radians * 57.2957795f; }
inline double degrees(double radians) { return radians * 57.29577951308232286465; }
inline float radians(float degrees) { return degrees * 0.01745329f; }
inline double radians(double degrees) { return degrees * 0.01745329251994329547; }

inline Vector
Point::operator-(const Point& r) const
{
	return Vector(data_ - r.data_);
}

inline Vector
Point::toVector() const
{
	return Vector(data_);
}

inline Point
Point::operator+(const Vector& r) const
{
	return Point(data_ + r.data_);
}

inline void
Point::operator+=(const Vector& r)
{
	data_ += r.data_;
}

inline Point
Point::operator-(const Vector& r) const
{
	return Point(data_ - r.data_);
}

inline void
Point::operator-=(const Vector& r)
{
	data_ -= r.data_;
}

inline Xform
Xform::zAlign(const Point& p, const Vector& v)
{
	return zAlign(p, p + v);
}

inline std::ostream&
operator<<(std::ostream& os, const Point& p)
{
	return os << p.data_;
}

inline std::ostream&
operator<<(std::ostream& os, const Vector& v)
{
	return os << v.data_;
}

inline bool
BBox::inside(const Point& xyz) const
{
	for (Point::size_type i = 0; i < 3; ++i)
		if (xyz[i] < llf[i] || xyz[i] > urb[i])
			return false;
	return true;
}

inline void
BBox::add(const Point& xyz)
{
	for (Point::size_type i = 0; i < 3; ++i)
		if (llf[i] > xyz[i])
			llf[i] = xyz[i];
		else if (urb[i] < xyz[i])
			urb[i] = xyz[i];
}

inline bool
Xform::isIdentity() const
{
	return isIdentity_;
}

inline std::ostream&
operator<<(std::ostream& os, const Xform& t)
{
	return os
	    << t.rot[0][0] << ' ' << t.rot[0][1] << ' ' << t.rot[0][2] << ' '
	    << t.xlate[0] << std::endl
	    << t.rot[1][0] << ' ' << t.rot[1][1] << ' ' << t.rot[1][2] << ' '
	    << t.xlate[1] << std::endl
	    << t.rot[2][0] << ' ' << t.rot[2][1] << ' ' << t.rot[2][2] << ' '
	    << t.xlate[2] << std::endl;
}

} // namespace Geom3d

inline Geom3d::Point
lerp(const Geom3d::Point& l, const Geom3d::Point& r, Geom3d::Real alpha)
{
	return Geom3d::Point(lerp(l.data(), r.data(), alpha));
}

inline Geom3d::Vector
lerp(const Geom3d::Vector& l, const Geom3d::Vector& r, Geom3d::Real alpha)
{
	return Geom3d::Vector(lerp(l.data(), r.data(), alpha));
}

inline Geom3d::Vector
combine(const Geom3d::Vector& l, const Geom3d::Vector& r, Geom3d::Real alpha,
							Geom3d::Real beta)
{
	return Geom3d::Vector(combine(l.data(), r.data(), alpha, beta));
}

inline Geom3d::Real
sqdistance(const Geom3d::Point& l, const Geom3d::Point& r)
{
	return sqdistance(l.data(), r.data());
}

inline Geom3d::Real
distance(const Geom3d::Point& l, const Geom3d::Point& r)
{
	return distance(l.data(), r.data());
}

inline Geom3d::Vector
cross(const Geom3d::Vector& l, const Geom3d::Vector& r)
{
	return Geom3d::Vector(cross(l.data(), r.data()));
}

namespace Geom3d {

inline Point
BBox::center() const
{
	return otf::lerp(llf, urb, 0.5);
}

inline Real
Point::distance(const Point& r) const
{
	return otf::distance(*this, r);
}

inline Real
Point::sqdistance(const Point& r) const
{
	return otf::sqdistance(*this, r);
}

} // namespace Geom3d

} // namespace otf

#endif
