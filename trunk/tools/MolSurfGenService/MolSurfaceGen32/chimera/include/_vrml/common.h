// --- UCSF Chimera Copyright ---
// Copyright (c) 2000 Regents of the University of California.
// All rights reserved.  This software provided pursuant to a
// license agreement containing restrictions on its disclosure,
// duplication and use.  This notice must be embedded in or
// attached to all copies, including partial copies, of the
// software or any revisions or derivations thereof.
// --- UCSF Chimera Copyright ---
//
// $Id: common.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef VRML_COMMON
# define VRML_COMMON

# ifdef NO_RTTI
#  define	DECL_RTTI \
	private: static const char *rtti_classType_;\
	public: static const char *rtti_classType() { return rtti_classType_; }\
	virtual const char *rtti_instType() const { return rtti_classType(); }
#  define	DEF_RTTI(C) \
	const char * C::rtti_classType_ = #C;

template <class T>
void *
_DynamicCast(const char *t, const T *expr)
{
	if (expr == NULL)	
		return NULL;
	if (expr->rtti_instType() != t)
		return NULL;
	return (void *) expr;
}

#  define	DynamicCast(C, expr) \
		((C *) _DynamicCast(C::rtti_classType(), expr))
#  define	ConstDynamicCast(C, expr) \
		((const C *) _DynamicCast(C::rtti_classType(), expr))
#  define	ReinterpretCast(C, expr) \
		((C *) expr)

# else

#  define	DECL_RTTI
#  define	DEF_RTTI(C)
#  define	DynamicCast(C, expr)	dynamic_cast<C *>(expr)
#  define	ConstDynamicCast(C, expr)	dynamic_cast<const C *>(expr)
#  define	ReinterpretCast(C, expr)	reinterpret_cast<C *>(expr)

# endif

# if !defined(_WIN32)

#  if !defined(NeXT)
#  if !defined(__APPLE__)
#   include <values.h>
#  endif
#  endif

#  define VRML_IMEX

# else

#  ifdef _MSC_VER
#   pragma warning(disable:4786)
#  endif

#  ifndef VRML_DLL
#   define VRML_IMEX
#  elif defined(VRML_EXPORT)
#   define VRML_IMEX __declspec(dllexport)
#  else
#   define VRML_IMEX __declspec(dllimport)
#  endif

#  define WIN32_LEAN_AND_MEAN
#  define NOMINMAX 1
#  include <windows.h>

# endif

# include <stdio.h>
# include <stdlib.h>
# include <string.h>
# include <math.h>

# ifndef M_PI
#  define	M_PI	3.14159265f
# endif

# include <iostream>

# ifdef OPENGL
#  ifndef NO_CHIMERA
#   include <GfxInfo.h>
#  else
#   include <GL/gl.h>
#  endif
#  include <GL/glu.h>
# else
typedef float	GLfloat;
# endif

# if defined(MOTIF) || defined(GLUT)
#  define DISPLAY
# endif

namespace VRML {

struct stringLess {
	bool	operator()(const char *n1, const char *n2) const
				{ return strcmp(n1, n2) < 0; }
};

inline char *
dupString(const char *s)
{
	if (s == NULL)
		return NULL;
	char *cp = new char[strlen(s) + 1];
	(void) strcpy(cp, s);
	return cp;
}

inline void
tab(std::ostream &s, int indent)
{
	for (int i = 0; i != indent; ++i)
		s << "  ";
}

} // namespace VRML

# if defined(__BORLANDC__)
inline bool isatty(int) { return false; }
# endif

#endif
