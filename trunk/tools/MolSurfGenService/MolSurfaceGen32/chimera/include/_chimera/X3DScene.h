#ifndef Chimera_X3DScene_h
# define Chimera_X3DScene_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include "_chimera_config.h"
# include "LineType.h"
# include "Color.h"

namespace chimera {

class CHIMERA_IMEX X3DScene: public otf::WrapPyObj
{
public:
	X3DScene();

	// component names
	enum Component {
		// 3.0 components
		Core,
		DIS,			// Distributed interactive simulation
		EnvironmentalEffects, EnvironmentalSensor, EventUtilities,
		Geometry2D, Geometry3D, Geospatial, Grouping,
		H_Anim,			// Humanoid animation
		Interpolation,
		KeyDeviceSensor,
		Lighting,
		Navigation, Networking,
		NURBS,			// Non-rational B-Splines
		PointingDeviceSensor,
		Rendering,
		Scripting, Shape, Sound,
		Text, Texturing, Time,
		// additional 3.1 components
		CADGeometry, CubeMapTexturing, Shaders, Texturing3D,
		// additional 3.2 components
		Followers, Layering, Layout, RigidBodyPhysics,
		Num_Components
	};

	// say which X3D components are needed for a model
	void needComponent(Component name, int level);
	// return minumum version for needed components
	// X3D Version 3.0 is ISO/IEC 19775:2004
	// X3D Version 3.1 is ISO/IEC 19775:2004/Am1:2006
	// X3D Version 3.2 is ISO/IEC FDIS 19775-1:2008
	const char* version() const;
# ifndef WrapPy
	// write out component part of X3D header for Interchange profile
	void writeComponents(std::ostream& out, const std::string& indent) const;
# endif /* WrapPy */

	// resue lit Appearance of a single color
	void reuseAppearance(std::ostream& out, unsigned indent,
							const Color* color);
	// resue unlit Appearance of a single color
	void reuseUnlitAppearance(std::ostream& out, unsigned indent,
			const Color* color, float lineWidth, LineType lineType);
# ifndef WrapPy
	virtual PyObject* wpyNew() const;
# endif
private:
	// keep track of definitions, emitted prototypes
	typedef std::map<const Color *, std::string> ColorMap;
	ColorMap litMap;
	struct UnlitKey {
		const Color *color;
		float lineWidth;
		LineType lineType;
		bool operator<(const UnlitKey& k) const {
				if (color == NULL || k.color == NULL) {
					if (k.color != NULL)
						return true;
					if (lineWidth < k.lineWidth)
						return true;
					if (lineWidth == k.lineWidth)
						return lineType < k.lineType;
					return false;
				}
				if (*color < *k.color)
					return true;
				if (*color == *k.color) {
					if (lineWidth < k.lineWidth)
						return true;
					if (lineWidth == k.lineWidth)
						return lineType < k.lineType;
				}
				return false;
			}
	};
	typedef std::map<UnlitKey, std::string> UnlitColorMap;
	UnlitColorMap unlitMap;
	bool placeSphereProto;		// TODO
	bool placeCylinderProto;	// TODO

	typedef int ComponentLevels[Num_Components];
	ComponentLevels levels;

	mutable double my_version;
	static ComponentLevels full_3_0;
	static ComponentLevels full_3_1;
	static ComponentLevels full_3_2;
	static ComponentLevels interchange;
};

} // namespace chimera

#endif
