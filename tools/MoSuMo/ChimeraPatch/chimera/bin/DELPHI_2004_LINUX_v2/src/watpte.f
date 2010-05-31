	subroutine watpte(n,m,xo,line,x,y)
c
c want to write a pdb file for a set of points. this subroutine
c composes one line.
c
	dimension xo(3)
	character*80 line
	character*5 wnum
	character*4 cnum
	character*8 pnum
	character*12 pnum2
	integer n,m
c
c n=atom number, m=residue number, xo=position
c
	line=" "
	line(1:6)="ATOM  "
	line(18:20)="SC "
cwal	line(14:14)="O"
	write(wnum,310)n
	line(7:11)=wnum
	write(cnum,320)m
	line(23:26)=cnum
	write(pnum,330) xo(1)
	line(31:38)=pnum
	write(pnum,330) xo(2)
	line(39:46)=pnum
	write(pnum,330) xo(3)
	line(47:54)=pnum
	write(pnum2,340) x
	line(56:67)=pnum2
	write(pnum2,340)y
	line(69:80)=pnum2
310	format(i5)
320	format(i4)
330	format(f8.3)
340	format(g12.5)
c
	return
	end
