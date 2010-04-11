#ifndef Chimera_OSLAbbrModel_h
# define Chimera_OSLAbbrModel_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# include <vector>
# include <string>
# include <otf/Reg.h>
# include "Selectable.h"

namespace chimera {

class Model;

class CHIMERA_IMEX OSLAbbrModel : public OSLAbbrTest {
public:
	virtual bool	test(const Model *m) const = 0;
};

class CHIMERA_IMEX OSLAbbrModelId : public OSLAbbrModel {

	class Item {
		int		id_[2];
		int		subid_[2];
		bool		anyStartId_, anyStartSubid_;
		bool		anyEndId_, anyEndSubid_;
	public:
				Item(const std::string &startId,
					const std::string &endId,
					const std::string &startSubid,
					const std::string &endSubid,
					bool hasDot);
		bool		test(const Model *m) const;
	};

private:
	typedef std::vector<Item *>	Items;
	Items		ranges_;
public:
			OSLAbbrModelId(const OSLAbbreviation &a);
	virtual		~OSLAbbrModelId();
	virtual void	add(const std::string &left,
				const std::string &right,
				bool hasDot);
	virtual bool	test(const Model *m) const;
public:
	static std::string	ident(const Model *m);
};

class CHIMERA_IMEX OSLAbbrModelName : public OSLAbbrModel {

	class Item {
		otf::Reg	*name_;
		int		subid_[2];
		bool		anyStartSubid_, anyEndSubid_;
	public:
				Item(const std::string &name,
					const std::string &startSubid,
					const std::string &endSubid,
					bool hasDot);
				~Item();
		bool		test(const Model *m) const;
	};
private:
	typedef std::vector<Item *>	Items;
	Items		names_;
public:
			OSLAbbrModelName(const OSLAbbreviation &a);
	virtual		~OSLAbbrModelName();
	virtual void	add(const std::string &left,
				const std::string &right,
				bool hasDot);
	virtual bool	test(const Model *m) const;
public:
	static std::string	ident(const Model *m);
};

} // namespace chimera

# endif /* WrapPy */

#endif
