#ifndef Chimera_Selectable_h
# define Chimera_Selectable_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Reg.h>
# include <vector>
# include <string>
# include <map>
# include "_chimera_config.h"
# include "TrackChanges.h"

namespace chimera {

enum Selector {
	SelDefault, SelGraph, SelSubgraph, SelVertex, SelEdge,
	SelMolecule = SelGraph, SelResidue = SelSubgraph,
	SelAtom = SelVertex, SelBond = SelEdge
};

# ifndef WrapPy

class OSLAbbreviation;

class CHIMERA_IMEX OSLAbbrTest
{
public:
			OSLAbbrTest() { }
	virtual		~OSLAbbrTest() { }
	virtual void	add(const std::string &left,
				const std::string &right,
				bool hasDot);
protected:
	void		parseItems(const std::string &s);
	void		decodeItem(const std::string &s);
	void		decodeRange(const std::string &s, std::string &start,
					std::string &end);
};

# endif /* WrapPy */

class CHIMERA_IMEX OSLAbbreviation: public otf::WrapPyObj
{
	// holds generic abbreviation information
	// and class-specific objects deposited when abbreviation is evaluated
public:
	typedef std::map<std::string, OSLAbbrTest *> TestMap;
	typedef TestMap::const_iterator const_iterator;
	typedef TestMap::iterator iterator;
private:
	int		level_;
	std::string	abbr_;
	TestMap		map_;
public:
			OSLAbbreviation(int level, const std::string &abbr);
			~OSLAbbreviation();
	// ATTRIBUTE: level
	int		level() const { return level_; }
	// ATTRIBUTE: abbr
	const std::string &
			abbr() const { return abbr_; }
# ifndef WrapPy
	const_iterator	begin() const { return map_.begin(); }
	iterator	begin() { return map_.begin(); }
	const_iterator	end() const { return map_.end(); }
	iterator	end() { return map_.end(); }
	iterator	find(const std::string s) { return map_.find(s); }
	OSLAbbrTest	*&operator[](const std::string s) { return map_[s]; }
	static otf::Reg	*strToRE(const std::string &s, bool isRange=false,
				bool caseIndependent=true);
	static int	getInteger(const std::string &s);

	virtual PyObject* wpyNew() const;
# endif
};

class CHIMERA_IMEX Selectable: public otf::WrapPyObj
{
	// ABSTRACT
	// a mixin for selection/picking support
	static int	count_;
public:
	typedef std::vector<Selectable *> Selectables;
	virtual std::string oslIdent(Selector start = SelDefault,
					Selector end = SelDefault) const = 0;
	virtual Selectables oslChildren() const = 0;
	virtual Selectables oslParents() const = 0;
	virtual bool oslTestAbbr(OSLAbbreviation *a) const = 0;
	// Every subclass should implement a class level selLevel const
	// which holds oslLevel()'s return value.
	virtual Selector oslLevel() const = 0;
	static int count();
	Selectable();
	virtual ~Selectable();
# ifndef WrapPy
	virtual PyObject* wpyNew() const;
# endif
private:
	static TrackChanges::Changes *const
			changes;
};

# ifndef WrapPy

inline int
Selectable::count()
{
	return count_;
}

# endif /* WrapPy */

} // namespace chimera

#endif
