#ifndef Chimera_DisplayList_h
# define Chimera_DisplayList_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# include <map>
# include <vector>
# include <utility>
# include <otf/Geom3d.h>
# include "ColorGroup.h"
# include "Color.h"
# include "LineType.h"
# include "Selectable.h"
# include "LensViewer.h"
# include "BulkStorage.h"
# include <GfxInfo.h>

namespace chimera {

class Color;
class X3DScene;

using otf::Geom3d::Point;
using otf::Geom3d::Vector;
using otf::Geom3d::Real;

// DisplayList's cache non-coordinate based results of traversing
// the molecule.  In particular, they are used to presort based on
// material/texture.
//
// All of the objects passed by pointer to DisplayList are assumed to
// exists as long as the DisplayList needs access to them.  So for
// immediate mode that means as long as the DisplayList is used.  Otherwise,
// until after the first draw.

class DisplayList
{
public:
	DisplayList(bool immediate = false);
	~DisplayList();
	void	start();
	void	setLineType(LineType linetype);
	void	setWireStipple(const int fp[2]);
	void	addPoint(const Color *color, float size, const Selectable *sel,
				const Point *p);
	void	addLitPoint(const Color *color, float size, const Selectable *sel,
				const Point *p, const Vector *n);
	void	addSphere(const Color *color, float size, const Selectable *sel,
				const Point *p);
	void	addWire(const Color *color0, float size, const Selectable *sel,
				const Point *p0, const Color *color1,
				const Point *p1);
#ifdef SUPPORT_LIT_WIRES
	void	addLitWire(const Color *color0, float size,
				const Selectable *sel, const Point *p0,
				const Vector *n0, const Color *color1,
				const Point *p1, const Vector *n1);
#endif
	void	addCylinder(const Color *color0, float size,
				const Selectable *sel, const Point *p0,
				const Color *color1, const Point *p1);
	void	addDisk(const Color *color, float size, const Selectable *sel,
				const Point *p, const Vector *n);
	void	addDisk(const Color *color, float size, const Selectable *sel,
				const Point *p0, const Point *p1);
	// all label models must be the same (eg., NULL if otherwise different)
	void	addLabel(const Color *color, const Selectable *sel,
				const char *label, const Point *p,
				const Vector &offset, const Model *m);
	void	finish(bool pick);
	void	draw(const LensViewer *v, LensViewer::DrawPass pass) const;
	void	drawPick(const LensViewer *v) const;
	void	drawPickLabels(const LensViewer *v) const;
	typedef std::map<const Color *, std::string> ColorMap;
	void	x3dNeeds(/* INOUT*/ X3DScene *scene) const;
	void	x3dWrite(std::ostream &out, unsigned indent,
					/* INOUT*/ X3DScene *scene) const;

	typedef BulkStorage<Point> ExtraPointData;
	ExtraPointData	extraPoints;
	typedef BulkStorage<Vector> ExtraVectorData;
	ExtraVectorData	extraVectors;

	// NOTE: this types/structs are public becase some C++ compilers
	//	can't handle them being private.
	// temporary data structures for building display lists
	typedef const ColorGroup *CGKey;
	struct CGKeySort {
		// This is similar to ColorGroup::operator<, except that it
		// works on ColorGroup*'s.
		bool	operator()(CGKey a, CGKey b) const {
				if (a == NULL)
					return b != NULL;
				if (b == NULL)
					return false;
				if (typeid(*a) != typeid(*b))
					return typeid(*a).before(typeid(*b));
				// arbitrary order within subclass
				return a < b;
			}
	};
	typedef std::pair<CGKey, float> DLKey;	// "Color", Size
	struct DLKeySort {
		bool	operator()(const DLKey &a, const DLKey &b) const {
				CGKeySort s;
				if (s(a.first, b.first))
					return true;
				if (s(b.first, a.first))
					return false;
				return a.second < b.second;
			}
	};
	struct PointInfo {
		const Selectable *sel;
		const Color *color;
		const Point *coord;
		PointInfo() {}
		PointInfo(const Selectable *s, const Color *c, const Point *p)
			: sel(s), color(c), coord(p) {}
	};
	struct LitPointInfo {
		const Selectable *sel;
		const Color *color;
		const Point *coord;
		const Vector *normal;
		LitPointInfo() {}
		LitPointInfo(const Selectable *s, const Color *c, const Point *p, const Vector *n)
			: sel(s), color(c), coord(p), normal(n) {}
	};
	struct SphereInfo {
		const Selectable *sel;
		const Color *color;
		const Point *coord;
		float size;
		SphereInfo() {}
		SphereInfo(const Selectable *s, const Color *c,
			const Point *p, float sz): sel(s), color(c),
			coord(p) , size(sz) {}
	};
	struct WireInfo {
		const Selectable *sel;
		const Color *color0;
		const Point *coord0;
		const Color *color1;
		const Point *coord1;
		WireInfo() {}
		WireInfo(const Selectable *s, const Color *c0,
			const Point *p0, const Color *c1, const Point *p1):
			sel(s), color0(c0), coord0(p0), color1(c1), coord1(p1)
			{}
	};
#ifdef SUPPORT_LIT_WIRES
	struct LitWireInfo {
		const Selectable *sel;
		const Color *color0;
		const Point *coord0;
		const Vector *normal0;
		const Color *color1;
		const Point *coord1;
		const Vector *normal1;
		LitWireInfo() {}
		LitWireInfo(const Selectable *s,
			const Color *c0, const Point *p0, const Vector *n0,
			const Color *c1, const Point *p1, const Vector *n1):
			sel(s), color0(c0), coord0(p0), normal0(n0),
			color1(c1), coord1(p1), normal1(n1)
			{}
	};
#endif
	struct CylInfo {
		const Selectable *sel;
		const Color *color0;
		const Point *coord0;
		const Color *color1;
		const Point *coord1;
		float size;
		CylInfo() {}
		CylInfo(const Selectable *s, const Color *c0, const Point *p0,
			const Color *c1, const Point *p1, float sz): sel(s),
			color0(c0), coord0(p0), color1(c1), coord1(p1),
			size(sz) {}
	};
	struct DiskInfo {
		const Selectable *sel;
		const Color *color;
		float size;
		const Point *coord;
		const Vector *normal;
		DiskInfo() {}
		DiskInfo(const Selectable *s, const Color *c, float sz,
						const Point *p, const Vector *n)
			: sel(s), color(c), size(sz), coord(p), normal(n) {}
	};
	struct LabelInfo {
		const Selectable *sel;
		const Color *color;
		const char *label;
		const Point *coord;
		Vector offset;
		mutable float scale;
		LabelInfo() {}
		LabelInfo(const Selectable *s, const Color *c, const char *l,
			const Point *p, const Vector &o):
			sel(s), color(c), label(l), coord(p), offset(o),
			scale(0) {}
	};
private:
	enum DLstate { Dirty, Empty, NonEmpty };
	mutable DLstate	dlState[LensViewer::NumDrawPass];
	GLuint	gldl;		// GL display list(s)
	int	dlCount;	// number of gl display lists
	LineType lineType;
	int	wireStipple[2];	// factor pattern
	bool	immediateMode;

	bool	drawOpaqueSurfaces() const;
	bool	drawLabels(const LensViewer *lv, bool picking = false) const;
	bool	drawLitLines() const;
	bool	drawUnlitLines() const;
	bool	drawTranslucent() const;
	void	makePick() const;

	typedef std::vector<PointInfo> piVec;
	typedef std::map<DLKey, piVec, DLKeySort> piData;
	mutable piData	points;		// temporary

	typedef std::vector<LitPointInfo> lpiVec;
	typedef std::map<DLKey, lpiVec, DLKeySort> lpiData;
	mutable lpiData	litPoints;	// temporary

	typedef std::vector<SphereInfo> siVec;
	typedef std::map<CGKey, siVec, CGKeySort> siData;
	mutable siData	spheres;	// temporary

	typedef std::vector<WireInfo> wiVec;
	typedef std::map<DLKey, wiVec, DLKeySort> wiData;
	mutable wiData	wires;		// temporary
#ifdef SUPPORT_LIT_WIRES
	typedef std::vector<LitWireInfo> lwiVec;
	typedef std::map<DLKey, lwiVec, DLKeySort> lwiData;
	mutable lwiData	litWires;	// temporary
#endif
	typedef std::vector<CylInfo> ciVec;
	typedef std::map<CGKey, ciVec, CGKeySort> ciData;
	mutable ciData	cylinders;	// temporary

	typedef std::vector<DiskInfo> diVec;
	typedef std::map<CGKey, diVec, CGKeySort> diData;
	mutable diData	disks;		// temporary

	typedef std::vector<LabelInfo> liVec;
	typedef std::map<CGKey, liVec, CGKeySort> liData;
	mutable liData	labels;		// temporary
	const Model	*labelModel;

	// billboard correction for all views
	mutable Xform bb_invmxf;	// inverse model-view transform
	mutable Real bb_angle;		// angle and
	mutable Vector bb_axis;		// axis of invmxf
};

} // namespace chimera

# endif /* WrapPy */

#endif
