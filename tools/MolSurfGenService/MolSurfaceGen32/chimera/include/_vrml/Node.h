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
// $Id: Node.h 28024 2009-07-07 20:22:50Z conrad $

#ifndef VRML_NODE
#define	VRML_NODE

#include "common.h"
#include "RefCount.h"
#include "Field.h"
#include "BoundingBox.h"
#include "Matrix.h"
#include "VrmlNodeType.h"
#include <map>

#ifdef OGLFONT
#include <_chimera/OGLFont.h>
#endif

namespace VRML {

static const int	FLUSH_SPHERE	= 0x1;
static const int	FLUSH_CYLINDER	= 0x2;
static const int	FLUSH_NURBS		= 0x4;
static const int	FLUSH_OTHER		= 0x8;
static const int	FLUSH_ALL		= 0xf;

const int			FONT_DEFAULT_SIZE = 400;
const float			FONT_DEFAULT_SCALE = 40.0;

class Scene;

typedef std::map<const char *, Field *, stringLess> FieldMap;

//
// Generic (or unrecognized) VRML node
//
class VRML_IMEX Node : public RefCount {
DECL_RTTI
protected:
	Scene			*scene_;
	VrmlNodeType	*type_;
	char			*name_;
public:
					Node(Scene *scene, VrmlNodeType *type);
	virtual			~Node();
	virtual void	print(std::ostream &s, int indent = 0) const;
	virtual void	x3dWrite(std::ostream &s, int indent = 0) const;
	virtual void	setName(const char *name);
	bool			hasErrorMessage() const;
	std::ostringstream &errorStream() const;
	virtual bool	legalChildNode() const;
	virtual bool	legalGeometryNode() const { return false; }
	const char *	name() const { return name_; }
	VrmlNodeType *	type() const { return type_; }
	const char *	typeName() const { return type_->getName(); }
	virtual const char *	x3dTypeName() const;
	Scene *			scene() const { return scene_; }
	virtual void	addField(Field * /*field*/) { return; }
	virtual void	deleteField(const char * /*name*/) { return; }
	virtual Field * fieldWithName(const char * /*name*/) const { return NULL; }
	virtual bool	check() const { return true; }
	virtual void	boundingBox(BoundingBox * /*bbox*/, const Matrix &/*m*/) const { return; }
	virtual void	finish() { return; }
public:
	static Node *	Create(Scene *scene, VrmlNodeType *type);
	static bool		LegalChildType(VrmlNodeType *type);
#ifdef OPENGL
public:
	virtual bool	render(bool /*ortho*/ = false) { return true; }
	virtual void	flushCache(int /*flushFlags*/) { return; }
#endif
};

//
// Output routine
//
inline std::ostream &	operator<<(std::ostream &s, const Node &node)
						{ node.print(s); return s; }



//
// Fake node created for USE statements
//
class VRML_IMEX NodeUse : public Node {
DECL_RTTI
protected:
	const char	*target_;
public:
					NodeUse(Scene *scene, const char *target);
	virtual			~NodeUse();
	virtual bool	legalChildNode() const;
	const char	*	targetName() const { return target_; }
	Node *			targetNode() const;
	virtual bool	check() const;
	virtual void	print(std::ostream &s, int indent = 0) const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
	virtual bool	render(bool ortho = false);
#endif
};



//
// Fake node created for PROTO statements
//
class VRML_IMEX NodeProto : public Node {
DECL_RTTI
public:
					NodeProto(Scene *scene, VrmlNodeType *type)
						: Node(scene, type) { return; }
	virtual bool	legalChildNode() const;
	virtual bool	check() const;
	virtual void	print(std::ostream &s, int indent = 0) const;
#ifdef OPENGL
	virtual bool	render(bool ortho = false);
#endif
};



//
// Base class for all recognized VRML nodes
//
class VRML_IMEX NodeData : public Node, public FieldMap {
DECL_RTTI
public:
					NodeData(Scene *scene, VrmlNodeType *type)
						: Node(scene, type) { return; }
	virtual			~NodeData();
	virtual void	addField(Field *field);
	virtual void	deleteField(const char *name);
	virtual Field *	fieldWithName(const char *name) const;
	virtual void	print(std::ostream &s, int indent = 0) const;
	virtual void	x3dWrite(std::ostream &s, int indent = 0) const;
	virtual void	finish();
private:
};



//
// Node created for instances of PROTO nodes
//
class VRML_IMEX NodeInstance : public NodeData {
DECL_RTTI
private:
	mutable Node *	expanded;
public:
					NodeInstance(Scene *scene, VrmlNodeType *type)
						: NodeData(scene, type), expanded(NULL) { return; }
	virtual			~NodeInstance();
	virtual void	x3dWrite(std::ostream &s, int indent = 0) const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
    Node *			expandedNode() const;
};


//
// Remainder of classes correspond to recognized VRML nodes
// (all subclasses of NodeData) and are listed in
// alphabetical order by node name
//
class VRML_IMEX NodeAnchor : public NodeData {
DECL_RTTI
public:
			NodeAnchor(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeAppearance : public NodeData {
DECL_RTTI
public:
			NodeAppearance(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
	virtual bool	check() const;
	virtual void	x3dWrite(std::ostream &s, int indent = 0) const;
#ifdef OPENGL
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeAudioClip : public NodeData {
DECL_RTTI
public:
			NodeAudioClip(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeBackground : public NodeData {
DECL_RTTI
public:
			NodeBackground(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeBillboard : public NodeData {
DECL_RTTI
protected:
	bool		freeRotation_;
	Vector		rotAxis_;
	Vector		localNormal_;
public:
			NodeBillboard(Scene *scene, VrmlNodeType *type);
	virtual		~NodeBillboard();
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
	virtual void	finish();
private:
	Matrix		undoMatrix(const Matrix &m, bool ortho) const;
#ifdef OPENGL
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeBox : public NodeData {
DECL_RTTI
public:
			NodeBox(Scene *scene, VrmlNodeType *type);
	virtual		~NodeBox();
	virtual bool	legalGeometryNode() const { return true; }
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flags);
#endif
};

class VRML_IMEX NodeCollision : public NodeData {
DECL_RTTI
public:
			NodeCollision(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeColor : public NodeData {
DECL_RTTI
public:
			NodeColor(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeColorInterpolator : public NodeData {
DECL_RTTI
public:
			NodeColorInterpolator(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeCone : public NodeData {
DECL_RTTI
public:
			NodeCone(Scene *scene, VrmlNodeType *type);
	virtual		~NodeCone();
	virtual bool	legalGeometryNode() const { return true; }
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeCoordinate : public NodeData {
DECL_RTTI
public:
			NodeCoordinate(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeCoordinateInterpolator : public NodeData {
DECL_RTTI
public:
			NodeCoordinateInterpolator(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeCylinder : public NodeData {
DECL_RTTI
public:
			NodeCylinder(Scene *scene, VrmlNodeType *type);
	virtual		~NodeCylinder();
	virtual bool	legalGeometryNode() const { return true; }
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeCylinderSensor : public NodeData {
DECL_RTTI
public:
			NodeCylinderSensor(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeDirectionalLight : public NodeData {
DECL_RTTI
public:
			NodeDirectionalLight(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeElevationGrid : public NodeData {
DECL_RTTI
public:
			NodeElevationGrid(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
	virtual bool	legalGeometryNode() const { return true; }
	virtual bool	check() const;
};

class VRML_IMEX NodeExtrusion : public NodeData {
DECL_RTTI
public:
			NodeExtrusion(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
	virtual bool	legalGeometryNode() const { return true; }
};

class VRML_IMEX NodeFog : public NodeData {
DECL_RTTI
public:
			NodeFog(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeFontStyle : public NodeData {
DECL_RTTI
public:
			NodeFontStyle(Scene *scene, VrmlNodeType *type);
	virtual		~NodeFontStyle();
#ifdef OGLFONT
protected:
	chimera::OGLFont *		font_;
	chimera::OGLFont::Style	style_;
	int						size_;
	float					spacing_;
public:
	virtual bool			render(bool ortho = false);
	virtual void			flushCache(int flushFlags);
private:
	virtual void			finish();
public:
	chimera::OGLFont *font() const { return font_; }
	int						size() const { return size_; }
	float					spacing() const { return spacing_; }
#endif
};

class VRML_IMEX NodeGroup : public NodeData {
DECL_RTTI
public:
			NodeGroup(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeImageTexture : public NodeData {
DECL_RTTI
public:
			NodeImageTexture(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeIndexedFaceSet : public NodeData {
DECL_RTTI
public:
			NodeIndexedFaceSet(Scene *scene, VrmlNodeType *type);
	virtual		~NodeIndexedFaceSet();
	virtual bool	legalGeometryNode() const { return true; }
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
protected:
	GLuint		listId_;
	bool		triangles;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeIndexedLineSet : public NodeData {
DECL_RTTI
public:
			NodeIndexedLineSet(Scene *scene, VrmlNodeType *type);
	virtual		~NodeIndexedLineSet();
	virtual bool	legalGeometryNode() const { return true; }
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeInline : public NodeData {
DECL_RTTI
public:
			NodeInline(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeLOD : public NodeData {
DECL_RTTI
public:
			NodeLOD(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
	virtual bool	check() const;
};

class VRML_IMEX NodeMaterial : public NodeData {
DECL_RTTI
public:
			NodeMaterial(Scene *scene, VrmlNodeType *type);
	virtual		~NodeMaterial();
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeMovieTexture : public NodeData {
DECL_RTTI
public:
			NodeMovieTexture(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeNavigationInfo : public NodeData {
DECL_RTTI
public:
			NodeNavigationInfo(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeNormal : public NodeData {
DECL_RTTI
public:
			NodeNormal(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeNormalInterpolator : public NodeData {
DECL_RTTI
public:
			NodeNormalInterpolator(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeNurbsCurve : public NodeData {
DECL_RTTI
public:
			NodeNurbsCurve(Scene *scene, VrmlNodeType *type);
	virtual		~NodeNurbsCurve();
	virtual bool	legalGeometryNode() const { return true; }
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeNurbsSurface : public NodeData {
DECL_RTTI
public:
			NodeNurbsSurface(Scene *scene, VrmlNodeType *type);
	virtual		~NodeNurbsSurface();
	virtual bool	legalGeometryNode() const { return true; }
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
	virtual void	x3dWrite(std::ostream &s, int indent = 0) const;
	virtual const char *	x3dTypeName() const;
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeOrientationInterpolator : public NodeData {
DECL_RTTI
public:
			NodeOrientationInterpolator(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodePixelTexture : public NodeData {
DECL_RTTI
public:
			NodePixelTexture(Scene *scene, VrmlNodeType *type);
	virtual		~NodePixelTexture();
#ifdef OPENGL
protected:
	GLuint		texture_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodePlaneSensor : public NodeData {
DECL_RTTI
public:
			NodePlaneSensor(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodePointLight : public NodeData {
DECL_RTTI
public:
			NodePointLight(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodePointSet : public NodeData {
DECL_RTTI
public:
			NodePointSet(Scene *scene, VrmlNodeType *type);
	virtual		~NodePointSet();
	virtual bool	legalGeometryNode() const { return true; }
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodePositionInterpolator : public NodeData {
DECL_RTTI
public:
			NodePositionInterpolator(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeProximitySensor : public NodeData {
DECL_RTTI
public:
			NodeProximitySensor(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeScalarInterpolator : public NodeData {
DECL_RTTI
public:
			NodeScalarInterpolator(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeScript : public NodeData {
DECL_RTTI
public:
			NodeScript(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeShape : public NodeData {
DECL_RTTI
public:
			NodeShape(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeSound : public NodeData {
DECL_RTTI
public:
			NodeSound(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
	virtual bool	check() const;
};

class VRML_IMEX NodeSphere : public NodeData {
DECL_RTTI
public:
			NodeSphere(Scene *scene, VrmlNodeType *type);
	virtual		~NodeSphere();
	virtual bool	legalGeometryNode() const { return true; }
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeSphereSensor : public NodeData {
DECL_RTTI
public:
			NodeSphereSensor(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeSpotLight : public NodeData {
DECL_RTTI
public:
			NodeSpotLight(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeSwitch : public NodeData {
DECL_RTTI
public:
			NodeSwitch(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeText : public NodeData {
DECL_RTTI
public:
			NodeText(Scene *scene, VrmlNodeType *type);
	virtual		~NodeText();
	virtual bool	legalGeometryNode() const { return true; }
	virtual bool	check() const;
#ifdef OGLFONT
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeTextureCoordinate : public NodeData {
DECL_RTTI
public:
			NodeTextureCoordinate(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeTextureTransform : public NodeData {
DECL_RTTI
public:
			NodeTextureTransform(Scene *scene, VrmlNodeType *type);
	virtual		~NodeTextureTransform();
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeTimeSensor : public NodeData {
DECL_RTTI
public:
			NodeTimeSensor(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeTouchSensor : public NodeData {
DECL_RTTI
public:
			NodeTouchSensor(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeTransform : public NodeData {
DECL_RTTI
public:
			NodeTransform(Scene *scene, VrmlNodeType *type);
	virtual		~NodeTransform();
	virtual bool	check() const;
	virtual void	boundingBox(BoundingBox *bbox, const Matrix &m) const;
#ifdef OPENGL
protected:
	GLuint		listId_;
public:
	virtual bool	render(bool ortho = false);
	virtual void	flushCache(int flushFlags);
#endif
};

class VRML_IMEX NodeViewpoint : public NodeData {
DECL_RTTI
public:
			NodeViewpoint(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeVisibilitySensor : public NodeData {
DECL_RTTI
public:
			NodeVisibilitySensor(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

class VRML_IMEX NodeWorldInfo : public NodeData {
DECL_RTTI
public:
			NodeWorldInfo(Scene *scene, VrmlNodeType *type)
					: NodeData(scene, type) { return; }
};

} // namespace VRML
#endif
