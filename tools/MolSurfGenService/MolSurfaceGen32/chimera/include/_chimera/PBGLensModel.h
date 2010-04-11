#ifndef Chimera_PBGLensModel_h
# define Chimera_PBGLensModel_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# include "Model.h"
# include "LensModel.h"
# include "Mol.h"

extern "C" {
typedef struct _object PyObject;
}

namespace chimera {

class Lens;
class ColorGroup;
class DisplayList;
class PseudoBondGroup;
class Color;

class PBGLensModel: public LensModel {
public:
	PBGLensModel(Lens *lens, PseudoBondGroup *pgp);
	virtual void	draw(const LensViewer *viewer, LensViewer::DrawPass pass) const;
	virtual void	drawPick(const LensViewer *viewer) const;
	virtual bool	validXform() const;
	virtual void	invalidateCache();
	virtual void	invalidateSelection();
	virtual void	x3dNeeds(/*INOUT*/ X3DScene *scene) const;
	virtual void	x3dWrite(std::ostream &out, unsigned indent,
					/*INOUT*/ X3DScene *scene) const;

	PseudoBondGroup	*model() const;

	void		updateColor(const Color *, const NotifierReason &);
	void		updateColorGroup(ColorGroup *, const NotifierReason &);
	void		updatePBG(const NotifierReason &);
private:
	// No remove function in Notifiers because we use one instance
	// for every instance we want to be notified about.
	class ColorNotifier: public Notifier {
	public:
		void update(const void *tag, void *cgInst,
					const NotifierReason &reason) const;
	};
	class ColorGroupNotifier: public Notifier {
	public:
		void update(const void *tag, void *cgInst,
					const NotifierReason &reason) const;
	};
	class PBGNotifier: public Notifier {
	public:
		void update(const void *tag, void *,
					const NotifierReason &reason) const;
	};

	virtual		~PBGLensModel();
	PseudoBondGroup	*pbg;
	mutable DisplayList	*dc;
	mutable bool		dirty;
	mutable DisplayList	*seldc;		// selection display cache
	mutable bool		dirtySelection;
	mutable ColorSet	colorsUsed;
	mutable ColorGroupSet	cgsUsed;
	ColorNotifier		colorNotifier;
	ColorGroupNotifier	cgNotifier;
	PBGNotifier		pbgNotifier;
	void		buildDisplayList(const LensViewer *) const;
};

} // namespace chimera

# endif /* WrapPy */

#endif
