#ifndef Chimera_OSLAbbrResidue_h
# define Chimera_OSLAbbrResidue_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# include <vector>
# include <string>
# include <otf/Reg.h>
# include "Selectable.h"

namespace chimera {

class Residue;

class CHIMERA_IMEX OSLAbbrResidue : public OSLAbbrTest {
public:
	virtual bool	test(const Residue *r) const = 0;
};

class CHIMERA_IMEX OSLAbbrResSeq : public OSLAbbrResidue {

	class Item {
		int		seq_[2];
		std::string	insert_[2];
		otf::Reg	*chain_, *caseChain_;
		bool		anySeq_[2];
	public:
				Item(const std::string &startLeft,
					const std::string &endLeft,
					const std::string &right,
					bool hasDot);
				~Item();
		bool		test(const Residue *r) const;
	private:
		void		parseSeq(const std::string &s, int n);
	};
private:
	typedef std::vector<Item *>	Items;
	Items		ranges_;
public:
			OSLAbbrResSeq(const OSLAbbreviation &a);
	virtual		~OSLAbbrResSeq();
	virtual void	add(const std::string &left,
				const std::string &right,
				bool hasDot);
	virtual bool	test(const Residue *r) const;
public:
	static std::string	ident(const Residue *r);
};

class CHIMERA_IMEX OSLAbbrResType : public OSLAbbrResidue {

	class Item {
		otf::Reg	*name_;
		otf::Reg	*chain_, *caseChain_;
	public:
				Item(const std::string &pat,
					const std::string &right,
					bool hasDot);
				~Item();
		bool		test(const Residue *r) const;
	};
private:
	typedef std::vector<Item *>	Items;
	Items		names_;
public:
			OSLAbbrResType(const OSLAbbreviation &a);
	virtual		~OSLAbbrResType();
	virtual void	add(const std::string &left,
				const std::string &right,
				bool hasDot);
	virtual bool	test(const Residue *r) const;
public:
	static std::string	ident(const Residue *r);
};

} // namespace chimera

# endif /* WrapPy */

#endif
