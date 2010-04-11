	subroutine wrtgcrg(gcrgnam,gcrglen,icount1b,gchrgp,gchrg,nmedia,
     &  scale,medeps,epkt)
c
	dimension gchrg(icount1b)
	integer gchrgp(3,icount1b),gcrglen,frmnum
	character*80 gcrgnam
c b+++++++++++++++++++++++
        real medeps(0:nmedia),epkt
c e++++++++++++++++++++++    
c
        open(20,file=gcrgnam(:gcrglen))
	frmnum=1
	write(20,*) "DELPHI OUTPUT FILE: GRID CHARGE"
	write(20,*) "FORMAT NUMBER=",frmnum
        write(20,*) "NUMBER OF CHARGES=",icount1b
c b+++++++++++++++
        do i = 0,nmedia
        write(20,*)'DIELECTRIC IN MEDIUM NUMBER ',i,' :',medeps(i)*epkt
        end do
c e+++++++++++++++                       
        write(20,*) "GRID SCALE=",scale
        do i=1,icount1b
        write(20,*)gchrg(i),gchrgp(1,i),gchrgp(2,i),gchrgp(3,i)
        end do
        close(20)
c
c
	end
