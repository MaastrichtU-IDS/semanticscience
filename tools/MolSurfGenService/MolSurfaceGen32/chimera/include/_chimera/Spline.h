#ifndef Chimera_Spline_h
# define Chimera_Spline_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

#include <otf/Geom3d.h>
#include "_chimera_config.h"
#include <stdexcept>

namespace chimera {

//
// Code is based on
//	Section 11.2, "Parametric Cubic Curves", in
//	Chapter 11, "Representing Curves and Surfaces", of
//	Computer Graphics, Principles and Practice,
//	Foley, van Dam, Feiner, Hughes
//	Second Edition,
//	Addison-Wesley Publishing Company, 1990.
//	pages 478-516.
//

typedef otf::Geom3d::Real		BasisMatrix[4][4];

class CHIMERA_IMEX GeometryVector {
	otf::Geom3d::Vector	vector_[4];
	// SEQUENCE METHODS
public:
				GeometryVector();
				GeometryVector(const GeometryVector &gv);
				GeometryVector(const otf::Geom3d::Vector &g0,
						const otf::Geom3d::Vector &g1,
						const otf::Geom3d::Vector &g2,
						const otf::Geom3d::Vector &g3);
	otf::Geom3d::Vector	&operator[](unsigned n) { return vector_[n]; }
	const otf::Geom3d::Vector
				&operator[](unsigned n) const
						{ return vector_[n]; }
	// at() is range-checked version of operator[]
	otf::Geom3d::Vector	&at(unsigned n) {
					if (n >= 4)
						throw std::out_of_range(
							"index out of range");
					return vector_[n];
				}
	const otf::Geom3d::Vector
				&at(unsigned n) const {
					if (n >= 4)
						throw std::out_of_range(
							"index out of range");
					return vector_[n];
				}
	const otf::Geom3d::Vector
				&vector(int n) const { return vector_[n]; }
	void			setVector(int n, const otf::Geom3d::Vector &v)
						{ vector_[n] = v; }
};

class CHIMERA_IMEX Spline {
	otf::Geom3d::Real	matrix_[4][3];
public:
	enum SplineType {
		BSpline, Bezier, Cardinal, Hermite
	};
public:
				Spline(SplineType basisType,
					const GeometryVector &geometry);
	virtual			~Spline(void);
	otf::Geom3d::Point	coordinate(otf::Geom3d::Real t) const;
	otf::Geom3d::Vector	tangent(otf::Geom3d::Real t) const;
private:
	void			apply(const otf::Geom3d::Real tvec[4],
					otf::Geom3d::Real answer[3]) const;
public:
	static GeometryVector	makeGeometryVector(SplineType basisType,
					const GeometryVector &cp);
};

# ifndef WrapPy

CHIMERA_IMEX extern BasisMatrix	BSplineBasis;
CHIMERA_IMEX extern BasisMatrix	BezierBasis;
CHIMERA_IMEX extern BasisMatrix	CardinalBasis;
CHIMERA_IMEX extern BasisMatrix	HermiteBasis;

# endif /* WrapPy */

} // namespace chimera

#endif
