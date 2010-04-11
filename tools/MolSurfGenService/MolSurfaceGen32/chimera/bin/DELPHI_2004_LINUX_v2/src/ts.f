	subroutine tops(xo,xu,crg,eps,sc, pot,trgelf,flag)
c
c	vars passed on to the subroutine
c	sc = float = scale at which we need potential
c	xo = float(3) = position of charge
c	crg = float = value of charge
c	phi = float (0:64,0:64,0:64) = potential map for lookup table
c	pot = float = potential we need
c	trgelf = float(3) = electric field at target point
c	flag = integer = 1 ==> calc. only potential
c		       = 2 ==> calc. only field
c		       = 3 ==> calc. both potential & field
c	
	real sc, crg, xo(3), xu(3), eps, trgelf(3), pot
	integer flag
c
c	vars used by the sub
c
	real v(8), dummy
	real axo(3), bxo(3), faxo(3), fbxo(3), crgrid(8), crgridpos(3,8)
	real axu(3), bxu(3), faxu(3), fbxu(3), trgridpos(3,8)
	real mfo(8), mfu(8), e(3), elf(3,8)
c
c#include "lookupmaps.h"
        real phi(0:64,0:64,0:64)
        logical rdlkphi
c
	integer vec(3), a(3), b(3), si
	integer i, j, k, l
	logical iex
c 		
	if (.not. rdlkphi) then
         inquire(file="lkphi.dat",exist=i
     &  ex)
         if(.not.iex) then
          write(6,*) "data file for analytic grid energy not present"
          goto 999
         end if
c
	write(6,*) "reading data file for analytic grid energies"
         open(14,file="lkphi.dat",
     &	form="unformatted")
          read(14) phi
         close(14)
	rdlkphi=.true.
        endif
c
c
        do i=1,3
	 axo(i) = float(int(xo(i)))
	 if (xo(i).lt.0.0) then
  	  bxo(i) = axo(i)-1.0
	 else
	  bxo(i) = axo(i)+1.0
	 endif
	end do
c
	do i=1,4
	 do j=1,3
	  crgridpos(j,i) = axo(j)
	 end do
	end do
c
	do i=5,8
	 crgridpos(3,i) = bxo(3)
	end do
c
	do i=1,2
	 crgridpos(i,7) = bxo(i)
        end do
        crgridpos(1,2)=bxo(1)
        crgridpos(2,4)=bxo(2)
        crgridpos(1,3)=bxo(1)
        crgridpos(2,3)=bxo(2)

 	do i=5,8
	 do j = 1,2
      	  crgridpos(j,i)= crgridpos(j,i-4)
   	 end do
     	end do
c
 	do i= 1,3
     	 faxo(i) = abs(xo(i)-axo(i))
	 fbxo(i) = abs(xo(i)-bxo(i))
	end do
c
        mfo(1) = fbxo(1)*fbxo(2)*fbxo(3)
	mfo(2) = faxo(1)*fbxo(2)*fbxo(3)
	mfo(3) = faxo(1)*faxo(2)*fbxo(3)
	mfo(4) = fbxo(1)*faxo(2)*fbxo(3)
	mfo(5) = fbxo(1)*fbxo(2)*faxo(3)
	mfo(6) = faxo(1)*fbxo(2)*faxo(3)
	mfo(7) = faxo(1)*faxo(2)*faxo(3)
	mfo(8) = fbxo(1)*faxo(2)*faxo(3)
c
	do i=1,8
	 crgrid(i) = crg*mfo(i)
	end do
c
c	crgrid(8) now contains the trilinearly interpolated charge at the eight
c	vertices surrounding the charge
c
	do i=1,3
	 axu(i) = float(int(xu(i)))
	 if (xu(i).lt.0.0) then
          bxu(i) = axu(i)-1.0
         else
          bxu(i) = axu(i)+1.0
         endif
	end do
c
	do i=1,4
	 do j=1,3
	  trgridpos(j,i) = axu(j)
	 end do
	end do
c
	do i=5,8
	 trgridpos(3,i) = bxu(3)
        end do
c
	do i=1,2
	 trgridpos(i,7) = bxu(i)
	end do
c
	trgridpos(1,2)=bxu(1)
	trgridpos(2,4)=bxu(2)
	trgridpos(1,3)=bxu(1)
	trgridpos(2,3)=bxu(2)
c
	do i=5,8
	 do j = 1,2
	  trgridpos(j,i)= trgridpos(j,i-4)
	 end do
	end do
c
        do i= 1,3
	 faxu(i) = abs(xu(i)-axu(i))
	 fbxu(i) = abs(xu(i)-bxu(i))
	end do
c
	mfu(1)= fbxu(1)*fbxu(2)*fbxu(3)
	mfu(2)= faxu(1)*fbxu(2)*fbxu(3)
	mfu(3)= faxu(1)*faxu(2)*fbxu(3)
	mfu(4)= fbxu(1)*faxu(2)*fbxu(3)
	mfu(5)= fbxu(1)*fbxu(2)*faxu(3)
	mfu(6)= faxu(1)*fbxu(2)*faxu(3)
	mfu(7)= faxu(1)*faxu(2)*faxu(3)
	mfu(8)= fbxu(1)*faxu(2)*faxu(3)
c
c	mfu contains the trilinear interpolation proportionality constants
c	for interpolating the potential onto the target point once we know the
c	potentials of the neighboring eight vertices to the target point
c
c	do i=1,8
c	 mfu(i) = mfu(i)*mfu(i)
c	end do
c
c
	if ((flag .eq. 1) .or. (flag .eq. 3)) then
	do i=1,8
	 v(i) = 0.0
	end do
	endif
	do i = 1,8
	 if (flag .gt.1) then
	  do j = 1,3
	   e(j)=0.0
	  end do
	 endif
	 do j = 1,8
	  if (abs(crgrid(j)).gt.1.e-6) then
 	   do k=1,3
	    vec(k) = trgridpos(k,i) - crgridpos(k,j)
	   end do
	   if (flag .ne. 2) then
	    dummy = phi(int(abs(vec(1))),int(abs(vec(2))),int(abs(vec(3)
     &  )))
	    dummy = dummy*crgrid(j)
	    v(i) =v(i)+dummy/eps*sc
	   endif
	   if (flag .gt. 1) then
	    do k = 1,3
	     si = 1
	     if (vec(k).lt.0) si = -1
	     do l=1,3
	      a(l) = int(abs(vec(l)))
	      b(l) = int(abs(vec(l)))
	     end do
	     if (a(k).lt.64) a(k)=a(k)+1
	     if (b(k).gt.0) then
	      b(k) = b(k)-1
	     else
	      b(k) = b(k) + 1
	     endif
	     dummy = (phi(a(1),a(2),a(3))-phi(b(1),b(2),b(3)))/eps*sc
c               dummy = (phi(a(1),a(2),a(3))-phi(b(1),b(2),b(3)))/2.00*sc
	     e(k)=e(k)-si*crgrid(j)*dummy
	    end do
	   endif
	  endif
	 end do
	 if (flag .gt. 1) then
	  do j=1,3
	   elf(j,i) = e(j)
	  end do
	 endif
	end do
c
	pot = 0.0
	do i = 1,8
	 pot = pot + v(i)*mfu(i)
	end do
c
	if (flag .gt. 1) then
	 do i=1,3
	  trgelf(i)=0.0
	 end do
c
	 do i=1,8
	  do j=1,3
	   trgelf(j) = trgelf(j) + elf(j,i)*mfu(i)
	  end do
	 end do
	endif
c
999	continue
	return
	end
