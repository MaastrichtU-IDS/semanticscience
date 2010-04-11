#ifndef otf_TmplResidue_h
#define	otf_TmplResidue_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <map>
#include <vector>
#include <otf/Symbol.h>
#include <otf/molkit/MolResId.h>
#include <otf/molkit/TAexcept.h>
#include "Residue_template.h"
#include <vector>
#include <otf/config.h>
#include <functional>
namespace otf { class TmplAtom; }

namespace otf {
class TmplMolecule;

class OTF_IMEX TmplResidue {
	friend class TmplMolecule;
	void	operator=(const TmplResidue &);	// disable
		TmplResidue(const TmplResidue &);	// disable
		~TmplResidue();
	std::map<otf::Symbol, TmplAtom *>	Atoms_;
public:
	void	addAtom(TmplAtom *element);
	void	removeAtom(TmplAtom *element);
	typedef std::vector<TmplAtom *> Atoms;
	inline Atoms atoms() const;
	typedef std::map<otf::Symbol, TmplAtom *> AtomsMap;
	inline const AtomsMap	&atomsMap() const;
	typedef std::vector<otf::Symbol> AtomKeys;
	inline AtomKeys	atomNames() const;
	TmplAtom	*findAtom(otf::Symbol) const;
public:
	inline otf::Symbol		type() const;
	inline void			setType(otf::Symbol t);
	inline const otf::MolResId	&id() const;
	inline bool			operator==(const TmplResidue &r) const;
	inline bool			operator<(const TmplResidue &r) const;
private:
	otf::Symbol	type_;
	otf::MolResId	rid;
public:
	// return atoms that received assignments from the template
	std::vector<TmplAtom *>	templateAssign(
				  void (*assignFunc)(TmplAtom *, const char *),
				  const char *app,
				  const char *templateDir,
				  const char *extension
				) const;
	std::vector<TmplAtom *>	templateAssign(
				  void (TmplAtom::*assignFunc)(const char *),
				  const char *app,
				  const char *templateDir,
				  const char *extension
				) const;
	std::vector<TmplAtom *>	templateAssign(assigner, 
				  const char *app,
				  const char *templateDir,
				  const char *extension
				) const;
private:
private:
	TmplAtom	*chief_, *link_;
	otf::Symbol	descrip_;
public:
	TmplAtom	*chief() const { return chief_; }
	void	chief(TmplAtom *a) { chief_ = a; }
	TmplAtom	*link() const { return link_; }
	void	link(TmplAtom *a) { link_ = a; }
	otf::Symbol	description() const { return descrip_; }
	void		description(otf::Symbol d) { descrip_ = d; }
private:
	TmplResidue(TmplMolecule *, otf::Symbol t, otf::MolResId rid);
	TmplResidue(TmplMolecule *, otf::Symbol t, otf::Symbol chain, int pos, char insert);
};

} // namespace otf

#endif
