#ifndef Chimera_Lens_h
# define Chimera_Lens_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

//	Copyright 1998 by the Regents of the University of California.
//	All rights reserved.  This software provided pursuant to a
//	license agreement containing restrictions on its disclosure,
//	duplication and use.  This notice must be embedded in or
//	attached to all copies, including partial copies, of the
//	software or any revisions or derivations thereof.
//
//	$Id: Lens.h 29406 2009-11-23 19:13:32Z gregc $

# include <vector>
# include <otf/WrapPy2.h>
# include <otf/Array.h>
# include <otf/Geom3d.h>
# include "_chimera_config.h"
# include "Notifier.h"
# include "TrackChanges.h"
# include "LensViewer.h"
# include "sphere.h"

# ifdef _WIN32
#  undef Type
# endif

namespace chimera {

class Lens;
class Model;
class LensModel;

typedef std::vector<Model *> ModelList;

# ifndef WrapPy

class CHIMERA_IMEX ScreenBox
{
	Lens	*lens_;
	int	box_[4];		// (orginX, originY, width, height)
public:
	ScreenBox(Lens *l, const int b[4]): lens_(l) {
		box_[0] = b[0]; box_[1] = b[1];
		box_[2] = b[2]; box_[3] = b[3];
	}
	void drawPick(const LensViewer *viewer);
	void drawPickLabels(const LensViewer *viewer);
	Lens	*lens() { return lens_; }
	int	*box() { return box_; }
};
typedef std::vector<ScreenBox> ScreenBoxes;

# endif /* WrapPy */

typedef std::vector<Lens *> Lenses;

class CHIMERA_IMEX Lens: public NotifierList, public otf::WrapPyObj
{
	// BASE CLASS
	Lens &operator=(const Lens &l);	// disable
	Lens(const Lens &l);		// disable
public:
	friend class ScreenBox;

	enum Type { Background, Opaque, Overlay };
	Lens(Type t);
	~Lens();
	// ATTRIBUTE: type
	Type		type();

	bool		active() const;
	void		setActive(bool a);

	static const unsigned int AT_END = ~0u;
	void		addLens(Lens *lens, unsigned int position = AT_END);
	void		shiftLens(Lens *lens, unsigned int position);
	void		removeLens(Lens *lens);
	// ATTRIBUTE: sublenses
	const Lenses	&sublenses() const;
	// ATTRIBUTE: parentLens
	// WEAKREF: parentLens
	Lens		*parentLens() const;

	virtual void	destroy();

# ifndef WrapPy
	virtual PyObject* wpyNew() const;

	virtual void	notify(const NotifierReason &reason) const;
	// notification reasons
	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	static Reason MODEL_CHANGE;
	static Reason ATTR_CHANGE;
	virtual void	wpyAssociate(PyObject* o) const;

	void		startFrame();
	void		draw(const LensViewer *viewer, LensViewer::DrawPass pass, const int box[4]);
	void		endFrame();
	void		computeScreenBoxes(const int box[4], int x, int y,
					bool pick, /*OUT*/ ScreenBoxes *bls);

	// Each element of FlattenLenses is a vector of lenses where the
	// first one is opaque and the rest are overlays.  These lenses
	// will be drawn as a group.

	struct FInfo;
	typedef std::vector<FInfo> FlattenLenses;

	// TraversalState -- keep track of information needed to get
	// sibling/uncle overlay lenses on top of an Opaque lens.

	struct CHIMERA_IMEX TraversalState {
		int bbls;	// index in FlattenLenses of ScreenBoxes
		unsigned int start;
		TraversalState(FlattenLenses *fl, int b);
	};
	typedef std::vector<TraversalState> TStates;

	struct CHIMERA_IMEX FInfo {
		ScreenBoxes bbls;
		TStates ts;	// temporary - copy of TraversalState stack
		FInfo(const ScreenBox &b, const TStates *t);
	};
	void		flattenLenses(const int box[4], FlattenLenses *fl);
# endif
	void		invalidateCache();
	void		invalidateSelectionCache();
	void		addModel(Model *m);
//TODO:	void		addModelFromLens(Lens *l, Model *m);
	void		removeModel(Model *m);
	// ATTRIBUTE: models
	void		models(/*OUT*/ ModelList *models) const;
# ifndef WrapPy
	void		drawModelBounds() const;
# endif

	const otf::Array<float, 4> &
			bounds() const;
# ifndef WrapPy
	void		setBounds(const float bounds[4]);
# endif
	void		setBounds(float llx, float lly, float width, float height);
	void		setLL(float llx, float lly);
	void		setSize(float width, float height);

# ifndef WrapPy
	void		updateSublens(Lens *sublens, const NotifierReason &);
	void		updateLensModel(LensModel *, const NotifierReason &);
	void		computeCurBox(const int box[4], int curbox[4]);
	void		drawPick(const LensViewer *v, const int curbox[4]);
	void		drawPickLabels(const LensViewer *v, const int curbox[4]);
# endif
private:
	friend class LensViewer;	// to access LensModels
	void		setParentLens(Lens *);

	class SublensNotifier: public Notifier {
	public:
		void update(const void *tag, void *,
					const NotifierReason &reason) const;
	};
	class LensModelNotifier: public Notifier {
	public:
		void update(const void *tag, void *lensModel,
					const NotifierReason &reason) const;
	};

	SublensNotifier		sublensNotifier;
	LensModelNotifier	lensModelNotifier;
	Type		type_;
	otf::Array<float, 4>
			bounds_;	// normalized llx, lly, width, height
	typedef std::vector<LensModel *> LensModels;
	LensModels	lensModels;
	Lens		*parentLens_;
	Lenses		sublenses_;
	bool		active_;
	static TrackChanges::Changes *const
			changes;
};

# ifndef WrapPy

inline void
ScreenBox::drawPick(const LensViewer *viewer)
{
	lens_->drawPick(viewer, box_);
}

inline void
ScreenBox::drawPickLabels(const LensViewer *viewer)
{
	lens_->drawPickLabels(viewer, box_);
}

inline Lens::Type
Lens::type()
{
	return type_;
}

inline bool
Lens::active() const
{
	return active_;
}

inline const otf::Array<float, 4> & Lens::bounds() const
{
	return bounds_;
}

inline Lens *
Lens::parentLens() const
{
	return parentLens_;
}

inline void
Lens::setParentLens(Lens *parent)
{
	parentLens_ = parent;
}

# endif /* WrapPy */

} // namespace chimera

#endif
