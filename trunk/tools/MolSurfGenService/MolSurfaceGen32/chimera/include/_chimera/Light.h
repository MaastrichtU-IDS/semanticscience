#ifndef Chimera_Light_h
# define Chimera_Light_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/Geom3d.h>
# include "_chimera_config.h"
# include "Notifier.h"
# include "TrackChanges.h"
# include "Color.h"

namespace chimera {

using otf::Geom3d::Point;
using otf::Geom3d::Vector;

class CHIMERA_IMEX Light: public NotifierList, public otf::WrapPyObj
{
	// ABSTRACT
	Light(const Light&);		// disable
	Light& operator=(const Light&);	// disable
public:
	Color		*diffuse() const;
	void		setDiffuse(/*NULL_OK*/ Color *c);
	float		diffuseScale() const;
	void		setDiffuseScale(float scale);
	Color		*specular() const;
	void		setSpecular(/*NULL_OK*/ Color *c);
	float		specularScale() const;
	void		setSpecularScale(float scale);
# ifndef WrapPy
	// projection and modelview matrices should be set before calling
	// draw and reset.
	virtual void	draw(int light) const;
	static void	reset(int light);
	virtual void	x3dWrite(std::ostream &out, unsigned indent) const = 0;

	virtual PyObject* wpyNew() const;

	virtual void	notify(const NotifierReason &reason) const;
	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	static Reason LIGHT_CHANGE;
# endif
	~Light();
protected:
	Light();
	static TrackChanges::Changes *const
			changes;
private:
	Color		*diff;
	Color		*spec;
	float		diffScale;
	float		specScale;
	void		updateColor(const Color *, const NotifierReason &);
	class ColorNotifier: public Notifier {
	public:
		void update(const void *tag, void *colorInst,
					const NotifierReason &reason) const;
		// No remove function because we use one instance for every
		// Color we want to be notified about.
	};
	friend class ColorNotifier;
	ColorNotifier	colorNotifier;
};

class CHIMERA_IMEX DirectionalLight: public Light
{
	DirectionalLight(const DirectionalLight&);		// disable
	DirectionalLight& operator=(const DirectionalLight&);	// disable
public:
	DirectionalLight();
	const Vector&	direction() const;
	void		setDirection(const Vector &dir);
# ifndef WrapPy
	virtual void	draw(int light) const;
	virtual void	x3dWrite(std::ostream &out, unsigned indent) const;

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
#endif
private:
	Vector		dir;
};

class CHIMERA_IMEX PositionalLight: public Light
{
	PositionalLight(const PositionalLight&);		// disable
	PositionalLight& operator=(const PositionalLight&);	// disable
public:
	PositionalLight();
	const Point&	position() const;
	void		setPosition(const Point &pos);
# ifndef WrapPy
	virtual void	draw(int light) const;
	virtual void	x3dWrite(std::ostream &out, unsigned indent) const;

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
#endif
private:
	Point		pos;
};

class CHIMERA_IMEX SpotLight: public PositionalLight
{
	SpotLight(const SpotLight&);			// disable
	SpotLight& operator=(const SpotLight&);		// disable
public:
	SpotLight();
	float		cutoff() const;
	void		setCutoff(float angle);	// 0-90 or 180 (default 180)
	const Vector&	direction() const;
	void		setDirection(const Vector &dir); // default (0, 0, -1)
	float		exponent() const;
	void		setExponent(float value); // 0-128 (default 0)
	typedef otf::Array<float, 3> Factors;
	const Factors&	attenuation() const;
# ifndef WrapPy
	void		setAttenuation(const Factors &factors);
# endif
	void		setAttenuation(float quadratic, float linear,
					float constant); // default 0, 0, 1
# ifndef WrapPy
	virtual void	draw(int light) const;
	virtual void	x3dWrite(std::ostream &out, unsigned indent) const;

	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
#endif
private:
	float		limit;
	Vector		dir;
	float		exp;
	Factors		factors;
};

inline Color* Light::diffuse() const { return diff; }
inline float Light::diffuseScale() const { return diffScale; }
inline Color* Light::specular() const { return spec; }
inline float Light::specularScale() const { return specScale; }

inline const Vector& DirectionalLight::direction() const { return dir; }
inline const Point& PositionalLight::position() const { return pos; }

inline float SpotLight::cutoff() const { return limit; }
inline const Vector& SpotLight::direction() const { return dir; }
inline float SpotLight::exponent() const { return exp; }
inline const SpotLight::Factors& SpotLight::attenuation() const { return factors; }

} // namespace chimera

#endif
