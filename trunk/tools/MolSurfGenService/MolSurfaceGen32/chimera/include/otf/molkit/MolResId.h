#ifndef otf_molkit_MolResId_h
# define otf_molkit_MolResId_h

// Copyright (c) 1996 The Regents of the University of California.
// All rights reserved.
// 
// Redistribution and use in source and binary forms are permitted
// provided that the above copyright notice and this paragraph are
// duplicated in all such forms and that any documentation,
// distribution and/or use acknowledge that the software was developed
// by the Computer Graphics Laboratory, University of California,
// San Francisco.  The name of the University may not be used to
// endorse or promote products derived from this software without
// specific prior written permission.
// 
// THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
// WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
// IN NO EVENT SHALL THE REGENTS OF THE UNIVERSITY OF CALIFORNIA BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
// OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF THIS SOFTWARE.

// $Id: MolResId.h 26655 2009-01-07 22:02:30Z gregc $

// residue sequence numbers

# include <otf/Symbol.h>

namespace otf {

class OTF_IMEX MolResId {
	Symbol	cid;			/* chain identifier */
	int	pos;			/* position */
	char	ic;			/* insertion code */
public:
	MolResId(): cid(" "), pos(0), ic(' ') {}
	MolResId(int pos, char insert = ' '): cid(" "), pos(pos), ic(insert) {
		if (ic == '\0')
			ic = ' ';
	}
	MolResId(Symbol chain, int pos, char insert = ' '):
					cid(chain), pos(pos), ic(insert) {
		if (cid.empty())
			cid = Symbol(" ");
		if (ic == '\0')
			ic = ' ';
	}
	MolResId(char chain, int pos, char insert = ' '): pos(pos), ic(insert) {
		if (chain == '\0')
			cid = Symbol(" ");
		else
			cid = Symbol(std::string(1, chain));
		if (ic == '\0')
			ic = ' ';
	}
	Symbol		chainId() const { return cid; }
	int		position() const { return pos; }
	char		insertionCode() const { return ic; }
	std::string	str() const;
	unsigned int	hash() const;
	bool		sameChain(const MolResId &rid) const;
	bool		operator<(const MolResId &rid) const;
	bool		operator<=(const MolResId &rid) const;
	bool		operator>(const MolResId &rid) const;
	bool		operator>=(const MolResId &rid) const;
	bool		operator==(const MolResId &rid) const;
	bool		operator!=(const MolResId &rid) const;
};

inline bool
MolResId::sameChain(const MolResId &rid) const
{
	return cid == rid.cid;
}

inline bool
MolResId::operator<(const MolResId &rid) const
{
	return cid < rid.cid || (cid == rid.cid && pos < rid.pos)
			|| (cid == rid.cid && pos == rid.pos && ic < rid.ic);
}

inline bool
MolResId::operator<=(const MolResId &rid) const
{
	return cid < rid.cid || (cid == rid.cid && pos < rid.pos)
			|| (cid == rid.cid && pos == rid.pos && ic <= rid.ic);
}

inline bool
MolResId::operator>(const MolResId &rid) const
{
	return cid > rid.cid || (cid == rid.cid && pos > rid.pos)
			|| (cid == rid.cid && pos == rid.pos && ic > rid.ic);
}

inline bool
MolResId::operator>=(const MolResId &rid) const
{
	return cid > rid.cid || (cid == rid.cid && pos > rid.pos)
			|| (cid == rid.cid && pos == rid.pos && ic >= rid.ic);
}

inline bool
MolResId::operator==(const MolResId &rid) const
{
	return cid == rid.cid && pos == rid.pos && ic == rid.ic;
}

inline bool
MolResId::operator!=(const MolResId &rid) const
{
	return cid != rid.cid || pos != rid.pos || ic != rid.ic;
}

inline std::ostream &
operator<<(std::ostream &os, const MolResId &rid)
{
	os << rid.str();
	return os;
}

} // namespace otf

#endif /* MolResId_h */
