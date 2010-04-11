#ifndef otf_molkit_Element_h
# define otf_molkit_Element_h

// Copyright (c) 1996-2009 The Regents of the University of California.
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

// $Id: Element.h 27577 2009-05-13 22:43:16Z gregc $

# include <otf/config.h>
# include <iostream>

namespace otf {

class OTF_IMEX Element {
public:
	// Atomic Symbols:
	enum AS {
		LonePair, H, D = 1, T = 1, He,
		Li, Be, B, C, N, O, F, Ne,
		Na, Mg, Al, Si, P, S, Cl, Ar,
		K, Ca, Sc, Ti, V, Cr, Mn, Fe, Co, Ni, Cu, Zn,
		Ga, Ge, As, Se, Br, Kr,
		Rb, Sr, Y, Zr, Nb, Mo, Tc, Ru, Rh, Pd, Ag, Cd,
		In, Sn, Sb, Te, I, Xe,
		Cs, Ba, La,
		Ce, Pr, Nd, Pm, Sm, Eu, Gd, Tb, Dy, Ho, Er, Tm, Yb, Lu,
		Hf, Ta, W, Re, Os, Ir, Pt, Au, Hg, Tl, Pb, Bi, Po, At, Rn,
		Fr, Ra, Ac,
		Th, Pa, U, Np, Pu, Am, Cm, Bk, Cf, Es, Fm, Md, No, Lr,
		Rf, Db, Sg, Bh, Hs, Mt, Ds, Rg,
		Uub, Uut, Uuq, Uup, Uuh, Uus, Uuo
	};
	static float	bondRadius(Element);
	static float	bondLength(Element, Element);
private:
	static AS	atomicNumber(const char *name);
	AS		as;		// atomic number
public:
	explicit Element(const char *name): as(atomicNumber(name)) {}
	explicit Element(int i): as(AS(i)) {}
		Element(AS a): as(a) {}
	const char	*name() const;
	int	number() const { return int(as); }
	float	mass() const;		// standard atomic weight
	long	hash() const { return number(); }
	bool	operator==(const Element &a) const { return as == a.as; }
	bool	operator!=(const Element &a) const { return as != a.as; }
	bool	operator<(const Element &a) const { return as < a.as; }
	bool	operator<=(const Element &a) const { return as <= a.as; }
	bool	operator>(const Element &a) const { return as > a.as; }
	bool	operator>=(const Element &a) const { return as >= a.as; }
};

inline std::ostream &
operator<<(std::ostream &os, const Element &a)
{
	os << a.name();
	return os;
}

} // namespace otf

#endif
