#ifndef Chimera_concave_h
# define Chimera_concave_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include "_chimera_config.h"
#include <GfxInfo.h>
#include <GL/glu.h>
#include <vector>

#ifndef WrapPy

class CHIMERA_IMEX GLConcavePolygon {
	class vertex {
	public:
		GLdouble	v[3];
		GLdouble	n[3];
				vertex(GLdouble x, GLdouble y, GLdouble z,
					GLdouble nx, GLdouble ny, GLdouble nz);
	};
	GLUtesselator		*tobj;
	typedef std::vector<vertex *>	VertexList;
	VertexList		vList;
	vertex		*_makeVertex(GLdouble x, GLdouble y, GLdouble z,
					GLdouble nx, GLdouble ny, GLdouble nz);
public:
			GLConcavePolygon();
			~GLConcavePolygon();
	void		begin();
	void		end();
	void		addVertex(GLdouble x, GLdouble y, GLdouble z,
					GLdouble nx, GLdouble ny, GLdouble nz);
	void		vertexCallback(void *vertex_data);
	void		combineCallback(GLdouble coords[3],
					void *vertex_data[4],
					GLfloat weight[4],
					void **dataOut);
};

inline
GLConcavePolygon::vertex::vertex(GLdouble x, GLdouble y, GLdouble z,
					GLdouble nx, GLdouble ny, GLdouble nz)
{
	v[0] = x;
	v[1] = y;
	v[2] = z;
	n[0] = nx;
	n[1] = ny;
	n[2] = nz;
}

#endif

#endif
