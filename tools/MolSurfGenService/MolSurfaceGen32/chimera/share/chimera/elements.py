# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: elements.py 26655 2009-01-07 22:02:30Z gregc $

from chimera import Element

name = [
	"LP",		# lone pair
	 "H", "He", "Li", "Be",  "B",  "C",  "N",  "O",  "F", "Ne",  # 1 - 10
	"Na", "Mg", "Al", "Si",  "P",  "S", "Cl", "Ar",  "K", "Ca",  # 11 - 20
	"Sc", "Ti",  "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",  # 21 - 30
	"Ga", "Ge", "As", "Se", "Br", "Kr", "Rb", "Sr",  "Y", "Zr",  # 31 - 40
	"Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "In", "Sn",  # 41 - 50
	"Sb", "Te",  "I", "Xe", "Cs", "Ba", "La", "Ce", "Pr", "Nd",  # 51 - 60
	"Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb",  # 61 - 70
	"Lu", "Hf", "Ta",  "W", "Re", "Os", "Ir", "Pt", "Au", "Hg",  # 71 - 80
	"Tl", "Pb", "Bi", "Po", "At", "Rn", "Fr", "Ra", "Ac", "Th",  # 81 - 90
	"Pa",  "U", "Np", "Pu", "Am", "Cm", "Bk", "Cf", "Es", "Fm",  # 91 - 100
	"Md", "No", "Lr",  # 101 - 103
]

LP = Element(Element.LonePair)
H = Element(Element.H)
He = Element(Element.He)
Li = Element(Element.Li)
Be = Element(Element.Be)
B = Element(Element.B)
C = Element(Element.C)
N = Element(Element.N)
O = Element(Element.O)
F = Element(Element.F)
Ne = Element(Element.Ne)
Na = Element(Element.Na)
Mg = Element(Element.Mg)
Al = Element(Element.Al)
Si = Element(Element.Si)
P = Element(Element.P)
S = Element(Element.S)
Cl = Element(Element.Cl)
Ar = Element(Element.Ar)
K = Element(Element.K)
Ca = Element(Element.Ca)
Sc = Element(Element.Sc)
Ti = Element(Element.Ti)
V = Element(Element.V)
Cr = Element(Element.Cr)
Mn = Element(Element.Mn)
Fe = Element(Element.Fe)
Co = Element(Element.Co)
Ni = Element(Element.Ni)
Cu = Element(Element.Cu)
Zn = Element(Element.Zn)
Ga = Element(Element.Ga)
Ge = Element(Element.Ge)
As = Element(Element.As)
Se = Element(Element.Se)
Br = Element(Element.Br)
Kr = Element(Element.Kr)
Rb = Element(Element.Rb)
Sr = Element(Element.Sr)
Y = Element(Element.Y)
Zr = Element(Element.Zr)
Nb = Element(Element.Nb)
Mo = Element(Element.Mo)
Tc = Element(Element.Tc)
Ru = Element(Element.Ru)
Rh = Element(Element.Rh)
Pd = Element(Element.Pd)
Ag = Element(Element.Ag)
Cd = Element(Element.Cd)
In = Element(Element.In)
Sn = Element(Element.Sn)
Sb = Element(Element.Sb)
Te = Element(Element.Te)
I = Element(Element.I)
Xe = Element(Element.Xe)
Cs = Element(Element.Cs)
Ba = Element(Element.Ba)
La = Element(Element.La)
Ce = Element(Element.Ce)
Pr = Element(Element.Pr)
Nd = Element(Element.Nd)
Pm = Element(Element.Pm)
Sm = Element(Element.Sm)
Eu = Element(Element.Eu)
Gd = Element(Element.Gd)
Tb = Element(Element.Tb)
Dy = Element(Element.Dy)
Ho = Element(Element.Ho)
Er = Element(Element.Er)
Tm = Element(Element.Tm)
Yb = Element(Element.Yb)
Lu = Element(Element.Lu)
Hf = Element(Element.Hf)
Ta = Element(Element.Ta)
W = Element(Element.W)
Re = Element(Element.Re)
Os = Element(Element.Os)
Ir = Element(Element.Ir)
Pt = Element(Element.Pt)
Au = Element(Element.Au)
Hg = Element(Element.Hg)
Tl = Element(Element.Tl)
Pb = Element(Element.Pb)
Bi = Element(Element.Bi)
Po = Element(Element.Po)
At = Element(Element.At)
Rn = Element(Element.Rn)
Fr = Element(Element.Fr)
Ra = Element(Element.Ra)
Ac = Element(Element.Ac)
Th = Element(Element.Th)
Pa = Element(Element.Pa)
U = Element(Element.U)
Np = Element(Element.Np)
Pu = Element(Element.Pu)
Am = Element(Element.Am)
Cm = Element(Element.Cm)
Bk = Element(Element.Bk)
Cf = Element(Element.Cf)
Es = Element(Element.Es)
Fm = Element(Element.Fm)
Md = Element(Element.Md)
No = Element(Element.No)
Lr = Element(Element.Lr)

metals = set()
for n in range(3,5): metals.add(Element(n))
for n in range(11,14): metals.add(Element(n))
for n in range(19,33): metals.add(Element(n))
for n in range(37,52): metals.add(Element(n))
for n in range(55,85): metals.add(Element(n))
for n in range(87,104): metals.add(Element(n))

alkaliMetals = set([Li, Na, K, Rb, Cs, Fr])
halides = set([F, Cl, Br, I])

def valence(e):
	if e.number == 1:
		return 1
	if e.number <= 20:
		return (e.number - 2) % 8
	if e.number <= 56:
		return (e.number - 18) % 18
	return (e.number - 54) % 32
