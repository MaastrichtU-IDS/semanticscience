#ifndef Chimera_MoleculeLensModel_h
# define Chimera_MoleculeLensModel_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# include "Model.h"
# include "LensModel.h"
// include Mol.h for Molecule.h
# include "Mol.h"
# include "ChainTrace.h"
# include "concave.h"

extern "C" {
typedef struct _object PyObject;
}

namespace chimera {

class Lens;
class ColorGroup;
class DisplayList;
class Color;
class PseudoBondGroup;

typedef std::vector<Point> Points;
typedef std::vector<Vector> Normals;
typedef std::vector<const Color *> Colors;


struct RingAromaticInfo
{
	Molecule::Atoms atoms;
	Real radius;
	const Color *color;
	Point center;
	Real angle;
	Vector axis;
	RingAromaticInfo(): radius(0), color(0), angle(0) {}
};

struct RingFillInfo
{
	Molecule::Atoms atoms;
	double radius;		// radius of cylinders
	const Color *single;	// non-NULL if single color
	Points tpoints;		// 3 points per triangle
	Normals tnormals;	// one normal per triangle
	Colors tcolors;		// one color per triangle
	Points cpoints;		// 2 points per cylinder
	Colors ccolors;		// 1 color per cylinder
	bool translucent;
	RingFillInfo(): radius(0), single(0), translucent(false) {}
};

// TODO: investigate further how bond rotations screw up caching

class MoleculeLensModel: public LensModel
{
public:
	MoleculeLensModel(Lens *lens, Molecule *molecule);
	virtual void	draw(const LensViewer *viewer, LensViewer::DrawPass pass) const;
	virtual void	drawPick(const LensViewer *viewer) const;
	virtual void	drawPickLabels(const LensViewer *viewer) const;
	virtual void	invalidateCache();
	virtual void	invalidateLOD();
	virtual void	invalidateSelection();
	virtual void	x3dNeeds(/*INOUT*/ X3DScene *scene) const;
	virtual void	x3dWrite(std::ostream &out, unsigned indent,
					/*INOUT*/ X3DScene *scene) const;

	Molecule	*model() const;

	void		updateModel(Model *, const NotifierReason &);
	void		updateColorGroup(ColorGroup *, const NotifierReason &);
	void		updateColor(const Color *, const NotifierReason &);
	void		updateLOD(const NotifierReason &);
private:
	class ModelNotifier: public Notifier {
	public:
		void update(const void *tag, void *model,
					const NotifierReason &reason) const;
	};
	class ColorGroupNotifier: public Notifier {
	public:
		void update(const void *tag, void *cgInst,
					const NotifierReason &reason) const;
	};
	class ColorNotifier: public Notifier {
	public:
		void update(const void *tag, void *colorInst,
					const NotifierReason &reason) const;
		// No remove function because we use one instance for every
		// Color we want to be notified about.
	};
	class LODNotifier: public Notifier {
	public:
		void update(const void *tag, void *lodInst,
					const NotifierReason &reason) const;
	};

	virtual		~MoleculeLensModel();
	Molecule	*mol;
	mutable DisplayList	*dc;
	mutable bool		dirty;
	mutable DisplayList	*seldc;		// selection display cache
	mutable bool		dirtySelection;
	mutable ColorGroupSet	cgsUsed;
	ColorGroupNotifier	cgNotifier;
	mutable ColorSet	colorsUsed;
	mutable bool		dirtyRibbon;
	mutable int		ribbonLOD;
	mutable GLuint		ribbonDL, ribbonTransDL;
	mutable GLuint		lowResDL;
	ColorNotifier	colorNotifier;
	ModelNotifier	modelNotifier;
	LODNotifier	lodNotifier;
	void		buildLowRes() const;
	void		buildDisplayList(const LensViewer *lv) const;
	void		buildRibbonDisplayList(const LensViewer *lv) const;
	struct RibbonInfo {
		std::vector<GLfloat> va;
		std::vector<GLfloat> na;
		std::vector<bool> front;
		bool closed;
		unsigned size;
		bool smoothLength;
		bool smoothWidth;
		bool capPrevious;
		Vector prevNormal;
		bool capNext;
		Vector nextNormal;
	};
	void		computeRibbon(Residue *residue, int steps,
				/*OUT*/ RibbonInfo *info) const;
	void		displayRibbon(Residue *r, const Color *color,
					int steps) const;

	mutable bool	dirtyRings;
	mutable GLuint	fillDL, fillLinesDL, fillTransDL;
	void		buildRingDisplayList(const LensViewer *lv) const;
	void		displayAromatic(const RingAromaticInfo &rai) const;
	void		displayFill(const RingFillInfo &rfi) const;
	void		computeRingInfo(const std::set<Bond *> &shownBonds) const;

	mutable ChainTrace	*chain;
	mutable GLConcavePolygon	concave;
	typedef std::vector<RingAromaticInfo> AromaticInfo;
	mutable AromaticInfo aromaticInfo;
	typedef std::vector<RingFillInfo> FillInfo;
	mutable FillInfo fillInfo;
};

} // namespace chimera

# endif /* WrapPy */

#endif
