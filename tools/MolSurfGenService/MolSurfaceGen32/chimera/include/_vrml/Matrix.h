// vi:set ts=4 sw=4:
// --- UCSF Chimera Copyright ---
// Copyright (c) 2000 Regents of the University of California.
// All rights reserved.  This software provided pursuant to a
// license agreement containing restrictions on its disclosure,
// duplication and use.  This notice must be embedded in or
// attached to all copies, including partial copies, of the
// software or any revisions or derivations thereof.
// --- UCSF Chimera Copyright ---
//
// $Id: Matrix.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef VRML_MATRIX
#define	VRML_MATRIX

#include "common.h"
#include <GL/gl.h>

namespace VRML {

class Vector {
protected:
	GLfloat		vector_[3];
public:
				Vector();
				Vector(const float v[3]);
				Vector(float x, float y, float z);
	GLfloat		&operator[](int n);
	GLfloat		operator[](int n) const;
	Vector		operator+(const Vector &v) const;
	float		operator*(const Vector &v) const;
	Vector		cross(const Vector &v) const;
	bool		normalize();
};

class Matrix {
protected:
	GLfloat		matrix_[16];
public:
				Matrix();	// returns identity matrix
				Matrix(float m[4][4]);
				Matrix(const GLfloat m[16]);
				operator const GLfloat *() const;
	GLfloat		&operator()(int r, int c);
	GLfloat		operator()(int r, int c) const;
	Matrix		operator*(const Matrix &right) const;
	Vector		operator*(const Vector &v) const;
	bool		operator==(const Matrix &m) const;
	bool		operator!=(const Matrix &m) const;
	float		difference(const Matrix &m) const;
public:
	static Matrix   Scale(float x, float y, float z);
	static Matrix   Translate(float x, float y, float z);
	static Matrix   Rotate(float radians, float x, float y, float z);
	static Matrix   Quaternion(float q[4]);
	static Matrix   VirtualSphere(float fx, float fy, float tx, float ty);
	static Matrix   InvertRotTran(const Matrix &m);
	static Matrix   InvertRot(const Matrix &m);
};

extern std::ostream &	operator<<(std::ostream &s, const Matrix &m);
extern std::ostream &	operator<<(std::ostream &s, const Vector &v);

//
// Implementation of Vector inlines
//

inline
Vector::Vector()
{
	vector_[0] = 0.0f;
	vector_[1] = 0.0f;
	vector_[2] = 0.0f;
}

inline
Vector::Vector(const float v[3])
{
	for (int i = 0; i != 3; ++i)
		vector_[i] = v[i];
}

inline
Vector::Vector(float x, float y, float z)
{
	vector_[0] = x;
	vector_[1] = y;
	vector_[2] = z;
}

inline GLfloat &
Vector::operator[](int n)
{
	return vector_[n];
}

inline GLfloat
Vector::operator[](int n) const
{
	return vector_[n];
}

inline Vector
Vector::operator+(const Vector &v) const
{
	return Vector(vector_[0] + v.vector_[0], vector_[1] + v.vector_[1],
					vector_[2] + v.vector_[2]);
}

inline float
Vector::operator*(const Vector &v) const
{
	float d = 0;
	for (int i = 0; i != 3; ++i)
		d += vector_[i] * v[i];
	return d;
}

inline Vector
Vector::cross(const Vector &v) const
{
	float result[3] = {
		vector_[1] * v[2] - vector_[2] * v[1],
		vector_[2] * v[0] - vector_[0] * v[2],
		vector_[0] * v[1] - vector_[1] * v[0]
	};
	return Vector(result);
}

inline bool
Vector::normalize()
{
	float l = (float) sqrt(*this * *this);
	if (l <= 0)
		return false;
	for (int i = 0; i != 3; ++i)
		vector_[i] /= l;
	return true;
}

//
// Implementation of Matrix inlines
//
inline
Matrix::Matrix()
{
	for (int i = 0; i != 16; ++i)
		matrix_[i] = (i % 5 == 0) ? 1.0f : 0.0f;
}

inline
Matrix::Matrix(float m[4][4])
{
	int n = 0;
	for (int i = 0; i != 4; ++i)
		for (int j = 0; j != 4; ++j)
			matrix_[n++] = m[i][j];
}

inline
Matrix::Matrix(const GLfloat m[16])
{
	for (int i = 0; i != 16; ++i)
		matrix_[i] = m[i];
}

inline
Matrix::operator const GLfloat *() const
{
	return matrix_;
}

inline GLfloat &
Matrix::operator()(int r, int c)
{
	return matrix_[r * 4 + c];
}

inline GLfloat
Matrix::operator()(int r, int c) const
{
	return matrix_[r * 4 + c];
}

inline Matrix
Matrix::operator*(const Matrix &right) const
{
	Matrix result;
	for (int i = 0; i != 4; ++i)
		for (int j = 0; j != 4; ++j) {
			float tmp = 0;
			for (int k = 0; k != 4; ++k)
				tmp += (*this)(i, k) * right(k, j);
			result(i, j) = tmp;
		}
	return result;
}

inline Vector
Matrix::operator*(const Vector &v) const
{
	Vector result((*this)(0, 3), (*this)(1, 3), (*this)(2, 3));
	for (int i = 0; i != 3; ++i)
		for (int j = 0; j != 3; ++j)
			result[i] += (*this)(i, j) * v[j];
	return result;
}

inline bool
Matrix::operator!=(const Matrix &m) const
{
	return !(*this == m);
}

} // namespace VRML

#endif
