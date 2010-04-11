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

// $Id: AtomType.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef AtomType_h
# define AtomType_h

# include <otfmisc/Symbol.h>

namespace otf {

class AtomType {
public:
	enum AT {
		Unknown,
		C3,	// sp3-hybridized carbon
		C2,	// sp2-hybridized carbon
		C1,	// sp-hybridized carbon
		Cac,	// carboxylate carbon
		N3P,	// sp3-hybridized nitrogen, formal positive charge
		N3,	// sp3-hybridized nitrogen, neutral
		Npl,	// sp2-hybridized nitrogen
		N1,	// sp-hybridized nitrogen
		Nox,	// N-oxide nitrogen
		Ntr,	// nitro nitrogen
		NgP,	// guanidinium nitrogen, partial positive charge
		O3,	// sp3-hybridized oxygen
		O2,	// sp2-hybridized oxygen
		OM,	// carboxylate or nitro oxygen, partial negative charge
		S3P,	// sp3-hybridized sulfer, partial positive charge
		S3,	// sp3-hybridized sulfer, neutral
		S2,	// sp2-hybridized sulfer
		Sac,	// sulfate sulfer
		Sox,	// sulfoxide or sulfone sulfer
		S,	// other sulfer
		Bac,	// borate boron
		Box,	// other oxidized boron
		B,	// other boron (not oxidized)
		Pac,	// phosphate phosphorus
		Pox,	// P-oxide phosphorus
		P3P,	// sp3-hybridized phosphours, partial positive charge
		P,	// other phosphours
		HC,	// hydrogen bonded to carbon
		H,	// other hydrogen
		DC,	// deuterium bonded to carbon
		D	// other deuterium
	};
private:
	static const char * const
			types[D + 1];
	Symbol		at;		// atomic number
public:
		AtomType(): at(types[Unknown]) {}
	explicit AtomType(const char *name): at(name) {}
	explicit AtomType(Symbol sym): at(sym) {}
	explicit AtomType(AT a) {
			if (a > D)
				at = Symbol(types[Unknown]);
			else
				at = Symbol(types[a]);
		}
	Symbol	name() const { return at; };
	bool	operator==(const AtomType &a) const { return at == a.at; }
	bool	operator!=(const AtomType &a) const { return at != a.at; }
	bool	operator<(const AtomType &a) const { return at <= a.at; }
	bool	operator<=(const AtomType &a) const { return at <= a.at; }
	bool	operator>(const AtomType &a) const { return at > a.at; }
	bool	operator>=(const AtomType &a) const { return at >= a.at; }
};

inline std::ostream &
operator<<(std::ostream &os, const AtomType &a)
{
	os << a.name();
	return os;
}

} // namespace otf

#endif
