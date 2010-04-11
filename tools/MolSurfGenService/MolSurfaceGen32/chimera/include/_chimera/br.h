#ifndef bondrot_br_h
# define bondrot_br_h

// Bond Rotation support

// Every root atom has its own componet.  Since there
// is a root atom for each component of the Molecule, there
// will be one for each bond rotation, ligand, -mer, water, etc.
// Many of these transformations will be the same (i.e., the
// identity transformation).

// Bond rotations can be nested.  Thus we need to maintain a
// transformation hierarchy.  The bond rotations are the glue
// between the transformations in the hierarchy.

# include <vector>
# include <otf/WrapPy2.h>
# include <otf/Geom3d.h>
# include "Notifier.h"
# include "TrackChanges.h"

namespace chimera {

using otf::Geom3d::Xform;

class Atom;
class Bond;
class Molecule;

class Component;
class Link;

struct CHIMERA_IMEX LinkDatum
{
	Link		*link;
	Bond		*bond;
	Atom		*atom;
	bool		parent;
	LinkDatum(Link *l, Bond *b, Atom *a, bool p):
					link(l), bond(b), atom(a), parent(p) {}
};
typedef std::vector<LinkDatum> LinkData;

class CHIMERA_IMEX Component
{
	// per-component (graph-wise) of molecule
	Component	&operator=(const Component &);	// disable
	Component(const Component &);			// disable
public:
	// TODO: if root Atom is deleted (or any other in component), we
	// need to potentially subdivide this component into many.  First
	// reset root to be root of parent's bond to component, then ....
	//
	Atom		*rootAtom;	// identifying Atom
	int		size;		// number of atoms in component
	int		totalSize;	// + number of atoms in children
	typedef std::vector<Link *> Links;
	Links		cChildren;
	Link		*cParent;

	Component(Atom *r, int sz):
			rootAtom(r), size(sz), totalSize(sz), cParent(0) {}
	void		saveLinkData(LinkData *data);
	void		split(const LinkData &data);
	void		adjustTotalSize(int delta);
	void		xform(const Xform &xf, Link *stop);
};

class CHIMERA_IMEX Link: public NotifierList, public otf::WrapPyObj
{
	Link	&operator=(const Link &);	// disable
	Link(const Link &);			// disable
public:
	// A link becomes invalid if it no longer separates a graph
	// (molecule) into several components or if its Atoms/Bonds
	// are deleted.
	//
	// Once a link is populated with all of its bonds, it should
	// call molecule->addLink(this).
	typedef std::vector<Component *> Components;
	Components lChildren;		// a BondRot only has one child
	Component *lParent;

	Link(Molecule *mol);
	virtual		~Link();
	Atom		*biggerSide() const;

	typedef std::vector<Bond *> Bonds;
	virtual const Bonds &
			bonds() const { return bonds_; }
	void		xformParent(const Xform &xf);
	void		xformChildren(const Xform &xf, Link *stop = NULL);

	virtual void	destroy();

	struct CHIMERA_IMEX Reason: public NotifierReason {
		Reason(const char *r): NotifierReason(r) {}
	};
	// notifier reasons
	static Reason CHANGED;

	virtual PyObject* wpyNew() const;
protected:
	void		addBond(Bond *element);
	Molecule*	molecule;
	static TrackChanges::Changes *const
			changes;
private:
	friend class Molecule;
	void		deletedBond(Bond *b);
	Bonds		bonds_;
};

class CHIMERA_IMEX BondRot: public Link
{
	// A specific kind of Link that for bond rotations.  Only one
	// bond is in the link.
	BondRot	&operator=(const BondRot &);	// disable
	BondRot(const BondRot &);		// disable
public:
	explicit	BondRot(Bond *b);
			~BondRot();
	double		angle() const;
	void		setAngle(double angle, Atom *anchor);
	void		adjustAngle(double delta, Atom *anchor);
	void		reset();
	virtual void	wpyAssociate(PyObject* o) const;
	virtual PyObject* wpyNew() const;
	virtual void	notify(const NotifierReason &reason) const;
private:
	// angle_ is from first atom towards second atom in bond
	double		angle_;
	Bond		*bond_;
	static TrackChanges::Changes *const
			changes;
};

# if 0
// TODO: a hinge cleaves a component into two parts
// TODO: how does one decide what the angle between the two parts is?
class CHIMERA_IMEX Hinge: public Link {
public:
	// TODO: would need way to get bonds back
	Hinge(Atom *one, Atom *two);
	double		angle() const;
	void		setAngle(double angle, Atom *anchor);
private:
	double		angle_;
};
# endif

}

#endif
