#ifndef Chimera_sphere_h
# define Chimera_sphere_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/Geom3d.h>
# include <vector>
# include "_chimera_config.h"

namespace chimera {

struct CHIMERA_IMEX Sphere {
	// IMPLICIT COPY CONSTRUCTOR
	const otf::Geom3d::Point& center() const;
	void	setCenter(const otf::Geom3d::Point& p);
	otf::Geom3d::Real radius() const;
	void	setRadius(otf::Geom3d::Real r);
	otf::Geom3d::Real radiusSq() const;
	void	setRadiusSq(otf::Geom3d::Real rsq);
	void	merge(const Sphere& s);
	void	xform(const otf::Geom3d::Xform& x);
	bool	inside(const otf::Geom3d::Point& xyz) const;
private:
	otf::Geom3d::Point m_center;
	otf::Geom3d::Real m_radius;
	otf::Geom3d::Real m_radius_sq;
};

#ifndef WrapPy
inline const otf::Geom3d::Point&
Sphere::center() const
{
	return m_center;
}

inline otf::Geom3d::Real
Sphere::radius() const
{
	return m_radius;
}

inline otf::Geom3d::Real
Sphere::radiusSq() const
{
	return m_radius_sq;
}
#endif

typedef std::vector<otf::Geom3d::Vector> SpherePts;

CHIMERA_IMEX extern const SpherePts &
		sphere_pts(float radius, float density);

} // namespace chimera

#endif
