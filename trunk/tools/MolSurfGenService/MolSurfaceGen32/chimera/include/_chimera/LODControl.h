#ifndef Chimera_LODControl_h
# define Chimera_LODControl_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include "_chimera_config.h"
# include "Notifier.h"

namespace chimera {

class CHIMERA_IMEX LODControl: public NotifierList, public otf::WrapPyObj
{
public:
	// Level Of Detail Control:
	//	Notifications are sent out whenever the pixelsPerUnit,
	//	quality, or tile scale changes.  pixelsPerUnit should be the
	//	number of pixels per length one OpenGL unit.  The quality
	//	is for tweaking how the pixelsPerUnit value is used --
	//	higher quality means higher subdivision.  The tile scale is
	//	for tiled rendering and should be set to ratio of the 
	//	resulting image width to the graphics window width.
	float		pixelsPerUnit() const;
	void		setPixelsPerUnit(float ppu);
	float		quality() const;
	void		setQuality(float q);
	float		tileScale() const;
	void		setTileScale(float tileScale);
	void		setQualityTileScale(float q, float tileScale,
				float fontAdust = 1);
					// only notify w/TILE_SCALE_CHANGE
	float		fontAdjust() const;
	float		adjustedTileScale() const;
	static LODControl *
			get();
#ifndef WrapPy
	virtual PyObject* wpyNew() const;

	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	// notifier reasons
	static Reason PPU_CHANGE;
	static Reason QUALITY_CHANGE;
	static Reason TILE_SCALE_CHANGE;
#endif
private:
	LODControl();
	float		ppu;		// pixels per unit
	float		q;		// quality
	float		ts;		// tile scale
	float		fa;		// font adjust
};

inline float
LODControl::pixelsPerUnit() const
{
	return ppu * ts;
}

inline float
LODControl::quality() const
{
	return q;
}

inline float
LODControl::tileScale() const
{
	return ts;
}

inline float
LODControl::fontAdjust() const
{
	return fa;
}

inline float
LODControl::adjustedTileScale() const
{
	return ts / fa;
}

} // namespace chimera

#endif
