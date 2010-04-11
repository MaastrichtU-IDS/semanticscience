	subroutine anasurf(sppos,icount2b,icount1b,ergu,scale)
c
	include 'qdiffpar4.h'
c
	dimension gchrg(icount1b),gpot(ngcrg)
	integer gchrgp(3,icount1b),sppos(3,icount2b)
	dimension phi(0:64,0:64,0:64)
	logical iex
c
	inquire(file="lkphi.dat",
     &	exist=iex) 
	if(.not.iex) then
	write(6,*) "data file for analytic reaction field energy 
     &	not present"
	goto 999
	end if
	open(14,file="lkphi.dat",
     &	form="unformatted")  
	read(14) phi
	close(14)
c
	do i=1,icount1b
	ix=gchrgp(1,i)
	iy=gchrgp(2,i)
	iz=gchrgp(3,i)
c
	gpot(i)=0.0
c
	do j=1,icount2b
	jx=sppos(1,j)
	jy=sppos(2,j)
	jz=sppos(3,j)
	kx=abs(ix-jx)
	ky=abs(iy-jy)
	kz=abs(iz-jz)
	gpot(i)=gpot(i)+phi(kx,ky,kz)*schrg(j)
	end do
c
	end do
c
	stot=0.0
	do i=1,icount2b
	stot=stot+schrg(i)
	end do
c
	do i=1,icount1b
	gpot(i)=gpot(i)*scale
	end do
c
	en=0.0
	do i=1,icount1b
	en=en+gpot(i)*gchrg(i)
	end do
c
	ergu=en
c
999	continue
	return
	end
