#ifndef Chimera_GfxHelp_h
# define Chimera_GfxHelp_h

# include "GfxInfo.h"
# include <otf/Geom3d.h>

# ifndef WrapPy
namespace GfxInfo {

using otf::Geom3d::Xform;
using otf::Geom3d::Real;

// MatrixStack makes sure that pushMatrix's are balanced with popMatrix's.

class MatrixStack
{
	// Scoped-based matrix stack state maintainer
	// Hooks for maintaining information about the matrix stack.
	// The idea is that we could enable/disable GL_NORMALIZE
	// if needed (currently Xform's don't scale nor shear)
	MatrixStack(const MatrixStack &ms);		// disable
	MatrixStack &operator=(const MatrixStack &ms);	// disable
public:
	MatrixStack() { glPushMatrix(); }
	void multiply(const Xform &xf);
	~MatrixStack() { glPopMatrix(); }
};

class MatrixGuard
{
	// fine-grained matrix stack guard
	// use to keep track of matrix stack changes so
	// if an exception is thrown, it gets cleaned up
	MatrixGuard(const MatrixGuard &ms);		// disable
	MatrixGuard &operator=(const MatrixGuard &ms);	// disable
	int counts[3];
public:
	MatrixGuard() { counts[0] = counts[1] = counts[2] = 0; }
	// argument should be one of GL_MODELVIEW, GL_PROJECTION, or GL_TEXTURE
	void push(GLenum type, bool switch_=false);
	void pop(GLenum type, bool switch_=false);
	void clear();
	~MatrixGuard() { clear(); }
};

class AttribGuard
{
	// fine-grained attribute stack guard
	// use to keep track of matrix stack changes so
	// if an exception is thrown, it gets cleaned up
	AttribGuard(const AttribGuard &ms);		// disable
	AttribGuard &operator=(const AttribGuard &ms);	// disable
	int count;
public:
	AttribGuard(): count(0) {}
	void push(GLbitfield mask) { ++count; glPushAttrib(mask); }
	void pop() { glPopAttrib(); --count; }
	~AttribGuard() { while (count--) glPopAttrib(); }
};

inline void
MatrixStack::multiply(const Xform &xf)
{
	if (xf.isIdentity())
		return;
	Real mat[16];
	xf.getOpenGLMatrix(mat);
	glMultMatrixd(mat);
}

inline void
MatrixGuard::push(GLenum type, bool switch_)
{
	++counts[type - GL_MODELVIEW];
	if (switch_)
		glMatrixMode(type);
	glPushMatrix();
}

inline void
MatrixGuard::pop(GLenum type, bool switch_)
{
	--counts[type - GL_MODELVIEW];
	if (switch_)
		glMatrixMode(type);
	glPopMatrix();
}

inline void
MatrixGuard::clear()
{
	int i;
	bool revert = false;
	if ((i = counts[GL_TEXTURE - GL_MODELVIEW]) > 0) {
		revert = true;
		glMatrixMode(GL_TEXTURE);
		while (i--)
			glPopMatrix();
		counts[GL_TEXTURE - GL_MODELVIEW] = 0;
	}
	if ((i = counts[GL_PROJECTION - GL_MODELVIEW]) > 0) {
		revert = true;
		glMatrixMode(GL_PROJECTION);
		while (i--)
			glPopMatrix();
		counts[GL_PROJECTION - GL_MODELVIEW] = 0;
	}
	if ((i = counts[GL_MODELVIEW - GL_MODELVIEW]) > 0) {
		if (revert) {
			glMatrixMode(GL_MODELVIEW);
			revert = false;
		}
		while (i--)
			glPopMatrix();
		counts[GL_MODELVIEW - GL_MODELVIEW] = 0;
	}
	if (revert)
		glMatrixMode(GL_MODELVIEW);
}

} // namespace GfxInfo
#endif

#endif
