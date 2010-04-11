	subroutine anagrd(icount1b,epsin,erga,scale)
	include 'qdiffpar4.h'
	dimension gchrg(icount1b),gpot(ngcrg),pot(ngcrg)
	integer gchrgp(3,icount1b)
	dimension phi(0:64,0:64,0:64)
	logical iex
c
c
	inquire(file="lkphi.dat",
     &	exist=iex)  
	if(.not.iex) then
        write(6,'(a40)') "data file for analytic grid energy not 
     &	present"
	goto 999
	end if
	open(14,file="lkphi.dat",
     &	form="unformatted")
	read(14) phi
	close(14)
c
c
	do i=1,icount1b
	gpot(i)=phi(0,0,0)*gchrg(i)
	end do
c
	do i=1,icount1b-1
	ix=gchrgp(1,i)
	iy=gchrgp(2,i)
	iz=gchrgp(3,i)
c
	do j=i+1,icount1b
	jx=gchrgp(1,j)
	jy=gchrgp(2,j)
	jz=gchrgp(3,j)
	kx=abs(ix-jx)
	ky=abs(iy-jy)
	kz=abs(iz-jz)
	pot(j)=phi(kx,ky,kz)
	end do
c
	gtemp=gchrg(i)
	temp=0.0
	do j=i+1,icount1b
	temp=temp+pot(j)*gchrg(j)
	gpot(j)=gpot(j)+pot(j)*gtemp
	end do
	gpot(i)=gpot(i) + temp
c
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
	erga=en/epsin
c
999	continue
	return
	end
