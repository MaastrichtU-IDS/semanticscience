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
// $Id: Scene.h 28024 2009-07-07 20:22:50Z conrad $

#ifndef VRML_SCENE
#define	VRML_SCENE

#include "common.h"
#include "RefCount.h"
#include "Node.h"
#include "BoundingBox.h"
#ifdef DISPLAY
#include "Matrix.h"
#endif

#include <vector>
#include <map>
#include <string>
#include <sstream>

#ifdef OGLFONT
#include <_chimera/OGLFont.h>
#endif

namespace VRML {

typedef void (*WalkNodeCB)(Node *node, void *closure);
typedef void (*WalkFieldCB)(Node *node, const char *name,
									Field *field, void *closure);

class VRML_IMEX Scene : public std::vector<Node *> {
public:
	enum CBEnum {
		Render,
		Flush,
		Export
	};
	struct ExportArgs {
		std::ostream &out;
		int indent;
		ExportArgs(std::ostream &s, int i): out(s), indent(i) {}
	};
	enum FCEnum {
		FC_None,
		FC_NamedColor
	};
	enum NCEnum {
		NC_None
	};
	typedef bool (*FieldCallback)(const Field &, int action, void *arg, void *closure);
private:
	static bool			FirstTime;
protected:
	static std::string	StandardNodeFile;
	typedef std::map<const char *, Node *, stringLess> NodeMap;
	typedef std::map<FCEnum, FieldCallback, std::less<FCEnum> > FCMap;
protected:
	NodeMap			nodeMap_;
	FCMap			fcMap_;
	void			*fClosure;
	int				debugLevel_;
	std::ostringstream		error_;
	std::string		location_;
public:
					Scene(std::istream &is, const char *location, int level = 0);
	virtual			~Scene();
	void			nameNode(Node *node);
	Node *			nodeWithName(const char *name) const;
	void			addNode(Node *node);

	bool			check();
	void			walk(WalkNodeCB fn, void *nodeClosure,
							WalkFieldCB ff, void *fieldClosure);
	void			clearError();
	void			print(std::ostream &s) const;
	void			x3dWrite(std::ostream &s, unsigned indent = 0) const;
	BoundingBox		boundingBox() const;

	std::string		location() const;
	std::string		errorMessage() const;
	bool			hasErrorMessage() const;
	std::ostringstream &errorStream();

	int				debugLevel() const;
	void			setDebug(int level);

	FieldCallback	setFieldCallback(FCEnum name, FieldCallback fc);
	FieldCallback	getFieldCallback(FCEnum name) const;
	void			*setFieldClosure(void *closure);
	void			*getFieldClosure() const;

protected:
	bool			readFile(const char *location, bool isStandard = false);
	bool			readStream(std::istream &is, const char *location, bool isStandard = false);
	void			walkNode(Node *node,
								WalkNodeCB fn, void *nodeClosure,
								WalkFieldCB ff, void *fieldClosure);
#ifdef OPENGL
protected:
	GLUquadric *	quadric_;
	int				slicesPerSphere_;
	int				stacksPerSphere_;
	int				slicesPerCylinder_;
	GLfloat			nurbsTolerance_;
	GLfloat			transparency_;
#ifdef OGLFONT
	mutable chimera::OGLFont	*font_;
	bool			hasTextNode_;
#endif
public:
	bool			render(bool ortho = false);
	GLUquadric *	quadric();
	int				slicesPerSphere() const;
	int				stacksPerSphere() const;
	int				slicesPerCylinder() const;
	GLfloat			nurbsTolerance() const;
	void			setSphereParam(int slices, int stacks);
	void			setCylinderParam(int slices);
	void			setNurbsTolerance(GLfloat t);
	void			setTransparency(GLfloat t);
	GLfloat			transparency() const;
#ifdef OGLFONT
	void			setHasTextNode();
	chimera::OGLFont	*font() { return font_; }
#endif
#endif
#ifdef DISPLAY
protected:
	int				width_, height_;
	int				vsphereCenterX_, vsphereCenterY_;
	float			vsphereRadius_;
	bool			rotating_;
	float			downX_, downY_;
	Matrix			downXform_;
	Matrix			xform_;
	BoundingBox		bbox_;
	float			center_[3], radius_;
	float			viewW_, viewH_;
	GLuint			bboxList_;
public:
	void			show(bool showBBox = false);
protected:
	void			openglInit();
	void			openglDraw();
	void			setWindowDimensions(int w, int h);
	void			buttonDown(int x, int y);
	void			buttonUp(int x, int y);
	void			buttonMotion(int x, int y);
	void			mapMouse(int x, int y, float *nx, float *ny);
protected:
	virtual void	wsInitialize() { }
	virtual void	wsMakeCurrent() { }
	virtual void	wsSwapbuffers() { }
	virtual void	wsMainloop() { }
#endif
};
inline std::string Scene::errorMessage() const
						{ return error_.str(); }
inline std::ostringstream &Scene::errorStream()
						{ return error_; }
inline int			Scene::debugLevel() const
						{ return debugLevel_; }
inline void			Scene::setDebug(int level)
						{ debugLevel_ = level; }
#ifdef OPENGL
inline void			Scene::setTransparency(float t)
						{ transparency_ = t; }
inline int			Scene::slicesPerSphere() const
						{ return slicesPerSphere_; }
inline int			Scene::stacksPerSphere() const
						{ return stacksPerSphere_; }
inline int			Scene::slicesPerCylinder() const
						{ return slicesPerCylinder_; }
inline GLfloat		Scene::nurbsTolerance() const
						{ return nurbsTolerance_; }
inline GLfloat		Scene::transparency() const
						{ return transparency_; }
#ifdef OGLFONT
inline void			Scene::setHasTextNode()
						{ hasTextNode_ = true; }
#endif
#endif

//
// Output routine
//
extern std::ostream &operator<<(std::ostream &s, const Scene &scene);

} // namespace VRML

#endif
