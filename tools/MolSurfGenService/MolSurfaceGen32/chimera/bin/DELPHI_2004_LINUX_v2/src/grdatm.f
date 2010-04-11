	subroutine grdatm(natom,igrid,scale,cmid)
	include 'pointer.h'
c
	real atpos(3,natom),xn2(3,natom),cmid(3)
c
	rmid=float((igrid+1)/2)
c  xn2 = atpos expressed  in grid units
	do 3104 i=1,natom
	xn2(1,i)=(atpos(1,i) -cmid(1))*scale + rmid
	xn2(2,i)=(atpos(2,i) -cmid(2))*scale + rmid
	xn2(3,i)=(atpos(3,i) -cmid(3))*scale + rmid
3104	continue 
c
	return
	end
