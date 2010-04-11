	subroutine watput(n,m,xo,line)
c
c want to write a pdb file for a set of points. this subroutine 
c composes one line.
c 
	dimension xo(3)
	character*80 line
	character*5 wnum
	character*3 cnum
	character*8 pnum
	integer n,m
c
c n=atom number, m=residue number, xo=position
c
	line=" "
	line(1:6)="ATOM  "
	line(18:20)="SP "
	line(14:14)="O"
	write(wnum,310)n
	line(7:11)=wnum
	write(cnum,320)m
	line(24:26)=cnum
	write(pnum,330)xo(1)
	line(31:38)=pnum
	write(pnum,330)xo(2)
	line(39:46)=pnum
	write(pnum,330)xo(3)
	line(47:54)=pnum
310	format(i5)
320	format(i3)
330	format(f8.3)
c
	return
	end
