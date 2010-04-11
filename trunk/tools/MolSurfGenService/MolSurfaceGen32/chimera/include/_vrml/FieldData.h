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
// $Id: FieldData.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef VRML_FIELDDATA
#define	VRML_FIELDDATA

#include "common.h"
#include <vector>

namespace VRML {

class VRML_IMEX FDBool {
protected:
	bool	value_;
public:
			FDBool();
	void	set(bool v);
	bool	get() const;
			operator bool() const;
	bool	operator==(const FDBool &other) const;
	bool	operator<(const FDBool &other) const;
};
inline		FDBool::FDBool() { value_ = false; }
inline void FDBool::set(bool v) { value_ = v; }
inline bool	FDBool::get() const { return value_; }
inline		FDBool::operator bool() const { return value_; }
inline bool FDBool::operator==(const FDBool &other) const
				{ return value_ == other.value_; }
inline bool FDBool::operator<(const FDBool &other) const
				{ return (int) value_ < (int) other.value_; }

class VRML_IMEX FDInt32 {
protected:
	int		value_;
public:
			FDInt32();
			FDInt32(int v);
	void	set(int v);
	int		get() const;
			operator int() const;
	bool	operator==(const FDInt32 &other) const;
};
inline		FDInt32::FDInt32() { value_ = 0; }
inline		FDInt32::FDInt32(int v) { value_ = v; }
inline void FDInt32::set(int v) { value_ = v; }
inline int	FDInt32::get() const { return value_; }
inline		FDInt32::operator int() const { return value_; }
inline bool FDInt32::operator==(const FDInt32 &other) const
				{ return value_ == other.value_; }

class VRML_IMEX FDFloat {
protected:
	GLfloat	value_;
public:
			FDFloat();
			FDFloat(GLfloat v);
	void	set(float v);
	GLfloat	get() const;
			operator GLfloat() const;
	bool	operator==(const FDFloat &other) const;
	bool	operator<(const FDFloat &other) const;
};
inline		FDFloat::FDFloat() { value_ = 0.0f; }
inline		FDFloat::FDFloat(GLfloat v) { value_ = v; }
inline void FDFloat::set(float v) { value_ = v; }
inline GLfloat
			FDFloat::get() const { return value_; }
inline		FDFloat::operator GLfloat() const { return value_; }
inline bool FDFloat::operator==(const FDFloat &other) const
				{ return value_ == other.value_; }
inline bool FDFloat::operator<(const FDFloat &other) const
				{ return value_ < other.value_; }

class VRML_IMEX FDImage {
protected:
	int		width_, height_, depth_;
	int		pixelsAdded_, pixelsMax_;
	unsigned char *
			pixels_;
public:
			FDImage();
			FDImage(const FDImage &v);
	virtual	~FDImage();
	void	setDimensions(int width, int height, int depth);
	int		width() const;
	int		height() const;
	int		depth() const;
	void *	pixels() const;
	void	addPixel(unsigned long pixel);
};
inline int		FDImage::width() const { return width_; }
inline int		FDImage::height() const { return height_; }
inline int		FDImage::depth() const { return depth_; }
inline void *	FDImage::pixels() const { return pixels_; }

class VRML_IMEX FDRotation {
protected:
	GLfloat	value_[4];
public:
			FDRotation();
	void	set(const float v[4]);
	const GLfloat *
			get() const;
			operator const GLfloat *() const;
	bool	operator==(const FDRotation &other) const;
	bool	operator<(const FDRotation &other) const;
	GLfloat	&operator[](int n);
	GLfloat	operator[](int n) const;

};
inline			FDRotation::FDRotation()
					{ value_[0] = value_[1] = value_[2] = value_[3] = 0.0f; }
inline void		FDRotation::set(const float v[3])
					{ value_[0] = v[0]; value_[1] = v[1];
					  value_[2] = v[2]; value_[3] = v[3]; }
inline const GLfloat *
				FDRotation::get() const { return value_; }
inline			FDRotation::operator const GLfloat *() const
					{ return value_; }
inline GLfloat &FDRotation::operator[](int n) { return value_[n]; }
inline GLfloat	FDRotation::operator[](int n) const { return value_[n]; }

class VRML_IMEX FDString {
protected:
	char	*value_;
public:
			FDString();
			FDString(const FDString &other);
	virtual	~FDString();
	void	set(const char *s);
	char *	get() const;
	FDString &
			operator=(const FDString &other);
			operator const char *() const;
	bool	operator==(const FDString &other) const;
	bool	operator<(const FDString &other) const;
};
inline		FDString::FDString() { value_ = NULL; }
inline char *
			FDString::get() const { return value_; }
inline		FDString::operator const char *() const { return value_; }
inline bool FDString::operator==(const FDString &other) const
				{ return strcmp(value_, other.value_) == 0; }
inline bool FDString::operator<(const FDString &other) const
				{ return strcmp(value_, other.value_) < 0; }

class VRML_IMEX FDVec2F {
protected:
	GLfloat	value_[2];
public:
			FDVec2F();
	void	set(const float v[2]);
	const GLfloat	*
			get() const;
			operator const GLfloat *() const;
	bool	operator==(const FDVec2F &other) const;
	bool	operator<(const FDVec2F &other) const;
	GLfloat	&operator[](int n);
	GLfloat	operator[](int n) const;

};
inline			FDVec2F::FDVec2F() { value_[0] = value_[1] = 0.0f; }
inline void		FDVec2F::set(const float v[2])
					{ value_[0] = v[0]; value_[1] = v[1]; }
inline const GLfloat *
				FDVec2F::get() const
					{ return value_; }
inline			FDVec2F::operator const GLfloat *() const
					{ return value_; }
inline GLfloat &FDVec2F::operator[](int n) { return value_[n]; }
inline GLfloat	FDVec2F::operator[](int n) const { return value_[n]; }

class VRML_IMEX FDVec3F {
protected:
	GLfloat	value_[3];
public:
			FDVec3F();
			FDVec3F(float x, float y, float z);
	void	set(const float v[3]);
	const GLfloat *
			get() const;
			operator const GLfloat *() const;
	bool	operator==(const FDVec3F &other) const;
	bool	operator<(const FDVec3F &other) const;
	GLfloat	&operator[](int n);
	GLfloat	operator[](int n) const;

};
inline			FDVec3F::FDVec3F()
					{ value_[0] = value_[1] = value_[2] = 0.0f; }
inline			FDVec3F::FDVec3F(GLfloat x, GLfloat y, GLfloat z)
					{ value_[0] = x;  value_[1] = y;  value_[2] = z; }
inline void		FDVec3F::set(const float v[3])
					{ value_[0] = v[0]; value_[1] = v[1];
					  value_[2] = v[2]; }
inline const GLfloat *
				FDVec3F::get() const
					{ return value_; }
inline			FDVec3F::operator const GLfloat *() const
					{ return value_; }
inline GLfloat &FDVec3F::operator[](int n)
					{ return value_[n]; }
inline GLfloat	FDVec3F::operator[](int n) const
					{ return value_[n]; }

typedef FDFloat FDTime;
typedef FDVec3F FDColor;
typedef std::vector<FDInt32> FDMFInt32;
typedef std::vector<FDFloat> FDMFFloat;
typedef std::vector<FDVec2F> FDMFVec2F;
typedef std::vector<FDVec3F> FDMFVec3F;
typedef std::vector<FDColor> FDMFColor;
typedef std::vector<FDRotation> FDMFRotation;

} // namespace VRML

#endif
