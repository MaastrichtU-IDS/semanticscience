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
// $Id: Field.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef VRML_FIELD
#define	VRML_FIELD

#include "common.h"
#include "RefCount.h"
#include "FieldData.h"
#include <vector>

namespace VRML {

class Node;

class VRML_IMEX Field : public RefCount {
DECL_RTTI
protected:
	int			error_;
	char		*name_;
public:
					Field(const char *name);
					Field(const Field &field);
	virtual			~Field();
	virtual Field *	clone() const;
	int				errorCount() const;
	void			setName(const char *name);
	const char		*name() const;
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
	virtual void	addSFBool(bool /*value*/)				{ error_++; }
	virtual void	addSFColor(const float /*value*/[3])	{ error_++; }
	virtual void	addMFColor(const float /*value*/[3])	{ error_++; }
	virtual void	addSFFloat(float /*value*/)				{ error_++; }
	virtual void	addMFFloat(float /*value*/)				{ error_++; }
	virtual void	addSFImageSize(int /*width*/, int /*height*/, int /*depth*/)
														{ error_++; }
	virtual void	addSFImage(int /*value*/)				{ error_++; }
	virtual void	addSFInt32(int /*value*/)				{ error_++; }
	virtual void	addMFInt32(int /*value*/)				{ error_++; }
	virtual void	addSFNode(Node * /*node*/)				{ error_++; }
	virtual void	addMFNode(Node * /*node*/)				{ error_++; }
	virtual void	addSFRotation(const float /*value*/[4])	{ error_++; }
	virtual void	addMFRotation(const float /*value*/[4])	{ error_++; }
	virtual void	addSFString(const char * /*value*/)		{ error_++; }
	virtual void	addMFString(const char * /*value*/)		{ error_++; }
	virtual void	addSFTime(float /*value*/)				{ error_++; }
	virtual void	addSFVec2F(const float /*value*/[2])	{ error_++; }
	virtual void	addMFVec2F(const float /*value*/[2])	{ error_++; }
	virtual void	addSFVec3F(const float /*value*/[3])	{ error_++; }
	virtual void	addMFVec3F(const float /*value*/[3])	{ error_++; }
	virtual void	addReference(const char *name)			{ error_++; }
public:
	static Field *	Create(int type, const char *name);
	static Field *	Clone(Field *field);
};
inline Field *		Field::clone() const { return NULL; }
inline int			Field::errorCount() const { return error_; }
inline const char *	Field::name() const { return name_; }



class VRML_IMEX SFBool : public Field, public FDBool {
DECL_RTTI
public:
					SFBool(const char *name);
					SFBool(const SFBool &v);
	virtual Field *	clone() const;
	virtual void	addSFBool(bool value);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		SFBool::SFBool(const char *name) : Field(name) { }
inline		SFBool::SFBool(const SFBool &v) : Field(v) { set(v.get()); }
inline Field *
			SFBool::clone() const { return new SFBool(*this); }
inline void SFBool::addSFBool(bool value) { set(value); }



class VRML_IMEX SFColor : public Field, public FDColor {
DECL_RTTI
public:
					SFColor(const char *name);
					SFColor(const SFColor &v);
	virtual Field *	clone() const;
	virtual void	addSFColor(const float value[3]);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		SFColor::SFColor(const char *name) : Field(name) { }
inline		SFColor::SFColor(const SFColor &v) : Field(v) { set(v.get()); }
inline Field *
			SFColor::clone() const { return new SFColor(*this); }
inline void SFColor::addSFColor(const float value[3]) { set(value); }



class VRML_IMEX MFColor : public Field, public std::vector<FDColor> {
DECL_RTTI
public:
					MFColor(const char *name);
					MFColor(const MFColor &v);
	virtual Field *	clone() const;
	virtual void	addMFColor(const float value[3]);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		MFColor::MFColor(const char *name) : Field(name) { }
inline		MFColor::MFColor(const MFColor &v)
					: Field(v), std::vector<FDColor>(v) { }
inline Field *
			MFColor::clone() const { return new MFColor(*this); }
inline void MFColor::addMFColor(const float value[3])
					{ FDColor c; c.set(value); push_back(c); }



class VRML_IMEX SFFloat : public Field, public FDFloat {
DECL_RTTI
public:
					SFFloat(const char *name);
					SFFloat(const SFFloat &v);
	virtual Field *	clone() const;
	virtual void	addSFFloat(float value);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		SFFloat::SFFloat(const char *name) : Field(name) { }
inline		SFFloat::SFFloat(const SFFloat &v) : Field(v) { set(v.get()); }
inline Field *
			SFFloat::clone() const { return new SFFloat(*this); }
inline void SFFloat::addSFFloat(float value) { set(value); }



class VRML_IMEX MFFloat : public Field, public std::vector<FDFloat> {
DECL_RTTI
public:
					MFFloat(const char *name);
					MFFloat(const MFFloat &v);
	virtual void	addMFFloat(float value);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		MFFloat::MFFloat(const char *name) : Field(name) { }
inline		MFFloat::MFFloat(const MFFloat &v)
					: Field(v), std::vector<FDFloat>(v) { }
inline void MFFloat::addMFFloat(float value)
					{ FDFloat f; f.set(value); push_back(f); }



class VRML_IMEX SFImage : public Field, public FDImage {
DECL_RTTI
public:
					SFImage(const char *name);
					SFImage(const SFImage &v);
	virtual Field *	clone() const;
	virtual void	addSFImageSize(int width, int height, int depth);
	virtual void	addSFImage(int value);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		SFImage::SFImage(const char *name) : Field(name) { }
inline		SFImage::SFImage(const SFImage &v) : Field(v), FDImage(v) { }
inline Field *
			SFImage::clone() const { return new SFImage(*this); }
inline void SFImage::addSFImageSize(int width, int height, int depth)
					{ setDimensions(width, height, depth); }
inline void SFImage::addSFImage(int value) { addPixel(value); }



class VRML_IMEX SFInt32 : public Field, public FDInt32 {
DECL_RTTI
public:
					SFInt32(const char *name);
					SFInt32(const SFInt32 &v);
	virtual Field *	clone() const;
	virtual void	addSFInt32(int value);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		SFInt32::SFInt32(const char *name) : Field(name) { }
inline		SFInt32::SFInt32(const SFInt32 &v) : Field(v) { set(v.get()); }
inline Field *
			SFInt32::clone() const { return new SFInt32(*this); }
inline void SFInt32::addSFInt32(int value) { set(value); }



class VRML_IMEX MFInt32 : public Field, public std::vector<FDInt32> {
DECL_RTTI
public:
					MFInt32(const char *name);
					MFInt32(const MFInt32 &v);
	virtual Field *	clone() const;
	virtual void	addMFInt32(int value);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		MFInt32::MFInt32(const char *name) : Field(name) { }
inline		MFInt32::MFInt32(const MFInt32 &v)
					: Field(v), std::vector<FDInt32>(v) { }
inline Field *
			MFInt32::clone() const { return new MFInt32(*this); }
inline void MFInt32::addMFInt32(int value)
					{ FDInt32 i; i.set(value); push_back(i); }



class VRML_IMEX SFNode : public Field {
DECL_RTTI
protected:
	Node			*node_;
public:
					SFNode(const char *name);
	virtual			~SFNode();
					// cannot clone
	Node			*node() const;
	virtual void	addSFNode(Node *node);
	virtual void	print(std::ostream &s, int indent) const;
};
inline Node * 		SFNode::node() const { return node_; }



class VRML_IMEX MFNode : public Field, public std::vector<Node *> {
DECL_RTTI
public:
					MFNode(const char *name);
	virtual			~MFNode();
					// cannot clone
	virtual void	addMFNode(Node *node);
	virtual void	print(std::ostream &s, int indent) const;
};



class VRML_IMEX SFRotation : public Field, public FDRotation {
DECL_RTTI
public:
					SFRotation(const char *name);
					SFRotation(const SFRotation &v);
	virtual Field *	clone() const;
	virtual void	addSFRotation(const float value[4]);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		SFRotation::SFRotation(const char *name)
					: Field(name) { }
inline		SFRotation::SFRotation(const SFRotation &v)
					: Field(v) { set(v.get()); }
inline Field *
			SFRotation::clone() const { return new SFRotation(*this); }
inline void SFRotation::addSFRotation(const float value[4]) { set(value); }



class VRML_IMEX MFRotation : public Field, public std::vector<FDRotation> {
DECL_RTTI
public:
					MFRotation(const char *name);
					MFRotation(const MFRotation &v);
	virtual Field *	clone() const;
	virtual void	addMFRotation(const float value[4]);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		MFRotation::MFRotation(const char *name)
					: Field(name) { }
inline		MFRotation::MFRotation(const MFRotation &v)
					: Field(v), std::vector<FDRotation>(v) { }
inline Field *
			MFRotation::clone() const { return new MFRotation(*this); }
inline void MFRotation::addMFRotation(const float value[4])
					{ FDRotation r; r.set(value); push_back(r); }



class VRML_IMEX SFString : public Field, public FDString {
DECL_RTTI
public:
					SFString(const char *name);
					SFString(const SFString &v);
	virtual Field *	clone() const;
	virtual void	addSFString(const char *value);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		SFString::SFString(const char *name)
					: Field(name) { }
inline		SFString::SFString(const SFString &v)
					: Field(v) { set(v.get()); }
inline Field *
			SFString::clone() const { return new SFString(*this); }
inline void SFString::addSFString(const char *value) { set(value); }



class VRML_IMEX MFString : public Field, public std::vector<FDString> {
DECL_RTTI
public:
					MFString(const char *name);
					MFString(const MFString &v);
	virtual Field *	clone() const;
	virtual void	addMFString(const char *value);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		MFString::MFString(const char *name)
					: Field(name) { }
inline		MFString::MFString(const MFString &v)
					: Field(v), std::vector<FDString>(v) { }
inline Field *
			MFString::clone() const { return new MFString(*this); }
inline void MFString::addMFString(const char *value)
					{ FDString s; s.set(value); push_back(s); }



class VRML_IMEX SFTime : public Field, public FDTime {
DECL_RTTI
public:
					SFTime(const char *name);
					SFTime(const SFTime &v);
	virtual Field *	clone() const;
	virtual void	addSFTime(float value);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		SFTime::SFTime(const char *name) : Field(name) { }
inline		SFTime::SFTime(const SFTime &v) : Field(v) { set(v.get()); }
inline Field *
			SFTime::clone() const { return new SFTime(*this); }
inline void SFTime::addSFTime(float value) { set(value); }



class VRML_IMEX SFVec2F : public Field, public FDVec2F {
DECL_RTTI
public:
					SFVec2F(const char *name);
					SFVec2F(const SFVec2F &v);
	virtual Field *	clone() const;
	virtual void	addSFVec2F(const float value[2]);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		SFVec2F::SFVec2F(const char *name) : Field(name) { }
inline		SFVec2F::SFVec2F(const SFVec2F &v) : Field(v) { set (v.get()); }
inline Field *
			SFVec2F::clone() const { return new SFVec2F(*this); }
inline void SFVec2F::addSFVec2F(const float value[2]) { set(value); }



class VRML_IMEX MFVec2F : public Field, public std::vector<FDVec2F> {
DECL_RTTI
public:
					MFVec2F(const char *name);
					MFVec2F(const MFVec2F &v);
	virtual Field *	clone() const;
	virtual void	addMFVec2F(const float value[2]);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		MFVec2F::MFVec2F(const char *name) : Field(name) { }
inline		MFVec2F::MFVec2F(const MFVec2F &v)
					: Field(v), std::vector<FDVec2F>(v) { }
inline Field *
			MFVec2F::clone() const { return new MFVec2F(*this); }
inline void MFVec2F::addMFVec2F(const float value[2])
					{ FDVec2F v; v.set(value); push_back(v); }



class VRML_IMEX SFVec3F : public Field, public FDVec3F {
DECL_RTTI
public:
					SFVec3F(const char *name);
					SFVec3F(const SFVec3F &v);
	virtual Field *	clone() const;
	virtual void	addSFVec3F(const float value[3]);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		SFVec3F::SFVec3F(const char *name) : Field(name) { }
inline		SFVec3F::SFVec3F(const SFVec3F &v) : Field(v) { set(v.get()); }
inline Field *
			SFVec3F::clone() const { return new SFVec3F(*this); }
inline void SFVec3F::addSFVec3F(const float value[3]) { set(value); }



class VRML_IMEX MFVec3F : public Field, public std::vector<FDVec3F> {
DECL_RTTI
public:
					MFVec3F(const char *name);
					MFVec3F(const MFVec3F &v);
	virtual Field *	clone() const;
	virtual void	addMFVec3F(const float value[3]);
	virtual void	print(std::ostream &s, int indent) const;
	virtual void	x3dWrite(std::ostream &s) const;
};
inline		MFVec3F::MFVec3F(const char *name) : Field(name) { }
inline		MFVec3F::MFVec3F(const MFVec3F &v)
					: Field(v), std::vector<FDVec3F>(v) { }
inline Field *
			MFVec3F::clone() const { return new MFVec3F(*this); }
inline void MFVec3F::addMFVec3F(const float value[3])
					{ FDVec3F v; v.set(value); push_back(v); }



class VRML_IMEX Reference : public Field, public FDString {
DECL_RTTI
public:
					Reference(const char *name);
					// cannot copy
					// cannot clone
	virtual void	addReference(const char *value);
	virtual void	print(std::ostream &s, int indent) const;
//	virtual void	x3dWrite(std::ostream &s) const;
//  x3dWrite should not be called for this class since we
//  print the expanded nodes and not the prototype instances.
};
inline		Reference::Reference(const char *name)
					: Field(name) { }
inline void Reference::addReference(const char *value) { set(value); }


//
// Utility functions
//
inline void addSFBool(Field *f, bool value)
					{ if (f) f->addSFBool(value); }
inline void addSFColor(Field *f, const float value[3])
					{ if (f) f->addSFColor(value); }
inline void addMFColor(Field *f, const float value[3])
					{ if (f) f->addMFColor(value); }
inline void addSFFloat(Field *f, float value)
					{ if (f) f->addSFFloat(value); }
inline void addMFFloat(Field *f, float value)
					{ if (f) f->addMFFloat(value); }
inline void addSFImageSize(Field *f, int width, int height, int depth)
					{ if (f) f->addSFImageSize(width, height, depth); }
inline void addSFImage(Field *f, int value)
					{ if (f) f->addSFImage(value); }
inline void addSFInt32(Field *f, int value)
					{ if (f) f->addSFInt32(value); }
inline void addMFInt32(Field *f, int value)
					{ if (f) f->addMFInt32(value); }
inline void addSFNode(Field *f, Node *node)
					{ if (f) f->addSFNode(node); }
inline void addMFNode(Field *f, Node *node)
					{ if (f) f->addMFNode(node); }
inline void addSFRotation(Field *f, const float value[4])
					{ if (f) f->addSFRotation(value); }
inline void addMFRotation(Field *f, const float value[4])
					{ if (f) f->addMFRotation(value); }
inline void addSFString(Field *f, const char *value)
					{ if (f) f->addSFString(value); }
inline void addMFString(Field *f, const char *value)
					{ if (f) f->addMFString(value); }
inline void addSFTime(Field *f, float value)
					{ if (f) f->addSFTime(value); }
inline void addSFVec2F(Field *f, const float value[2])
					{ if (f) f->addSFVec2F(value); }
inline void addMFVec2F(Field *f, const float value[2])
					{ if (f) f->addMFVec2F(value); }
inline void addSFVec3F(Field *f, const float value[3])
					{ if (f) f->addSFVec3F(value); }
inline void addMFVec3F(Field *f, const float value[3])
					{ if (f) f->addMFVec3F(value); }
inline void addReference(Field *f, const char *name)
					{ if (f) f->addReference(name); }

} // namespace VRML

#endif
