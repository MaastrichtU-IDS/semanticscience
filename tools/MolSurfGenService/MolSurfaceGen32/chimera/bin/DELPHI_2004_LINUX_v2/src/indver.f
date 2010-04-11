	subroutine indverdata(prbrad,scale)
	include 'acc2.h'
	real mxx,mxy,mxz,jig
c
c cba defines scale, cba and jig the box limits..
c note that cba is the minumum box size. it can be bigger if need be.
c i.e. can rescale to a larger box if need be.
c
	cba=prbrad
c	jig=(1.0/scale)
	jig=2.0*(1.0/scale)

	mnx=cmin(1)-rdmx-prbrad
	mny=cmin(2)-rdmx-prbrad
	mnz=cmin(3)-rdmx-prbrad
	mxx=cmax(1)+rdmx+prbrad
	mxy=cmax(2)+rdmx+prbrad
	mxz=cmax(3)+rdmx+prbrad
c
c accessible surface points are prbrad away from the actual surface
c mid points are at most (1/scale) away from the actual surface.
c midpoints must never be in box zero. accessible point can be in box zero
c but not in box -1.
c
c e.g. mnx+prbrad==van der Waals surface
c vanderwaals surface - (1/scale)= minumum midpoint position.
c therefore mnx+prbrad-(1/scale) gt 1
c and mnx gt 0. the latter is always true since cba is ge. prbrad.
c therefore we have...
c
c
	mxx=mxx+jig
	mxy=mxy+jig
	mxz=mxz+jig
	mnx=mnx-jig
	mny=mny-jig
	mnz=mnz-jig
c
100	mxx=mxx+cba-prbrad
	mxy=mxy+cba-prbrad
	mxz=mxz+cba-prbrad
	mnx=mnx-cba+prbrad
	mny=mny-cba+prbrad
	mnz=mnz-cba+prbrad
c
	il=int((mxx-mnx)/cba)+1
	im=int((mxy-mny)/cba)+1
	in=int((mxz-mnz)/cba)+1
c
c if points are too widely seperated for the scale and idmax then
c rescale..
	if((il.gt.idmax).or.(im.gt.idmax).or.(in.gt.idmax)) then
	idtemp=max(il,im,in)
	cba=cba*float(idtemp+1)/float(idmax)
	write(6,*) "initial cube size too small, "
	write(6,*) "in assigning accessible points to a grid"
	write(6,*) "therefore rescaling..."
	goto 100
	end if
	lcb1=il
	mcb1=im
	ncb1=in
c
c grdi is just the inverse of cba..,used more...
	grdi=1.0/cba

	return
	end
c
	subroutine indver(extot)
c
c program to compile the lists iab1,iab2 and icume for use in
c nearest vertex work. iexpos are box coordinates of vertices
c and dont need to be passed if comaprisons are done with real angstroms..
c but its often more convenient to do so since grid points have to be
c converted anyway...
c
	include 'acc2.h'
	integer iab1(0:lcb1,0:mcb1,0:ncb1),iab2(0:lcb1,0:mcb1,0:ncb1),
     &	icume(1)
	integer iexpos(3,1)
c
	i_iexpos= memalloc(i_iexpos,4*3*extot)
c
c initialize grid..
	do i=0,lcb1
	do j=0,mcb1
	do k=0,ncb1
	  iab1(i,j,k)=1
c         iab2(i,j,k)=0 no longer needed, calloc superseded malloc
	end do
	end do
	end do
c
c make linear arrays for expos
c
c find the number of points in each box, put in iab2, make iexpos
	do i=1,extot
	  x=(expos(1,i)-mnx)*grdi
	  ix=int(x)
	  y=(expos(2,i)-mny)*grdi
	  iy=int(y)
	  z=(expos(3,i)-mnz)*grdi
	  iz=int(z)
	  iab2(ix,iy,iz)=iab2(ix,iy,iz)+1
	  iexpos(1,i)=ix
	  iexpos(2,i)=iy
	  iexpos(3,i)=iz
	end do
c
c check each box for occupancy, using fill number to mark out
c space in icume, using
	n=0
	do i=0,lcb1
	do j=0,mcb1
	do k=0,ncb1
c
c if the box is not empty put start position to n+1 in iab1
c end to n+box occupancy in iab2, overwriting occupancy..
	if(iab2(i,j,k).ne.0) then
	iab1(i,j,k)=n+1
	n=n+iab2(i,j,k)
	iab2(i,j,k)=n
	end if
c
	end do
	end do
	end do
c
c fill icume using iab1 and iab2, note that iab1 is used to hold the
c position in icume, therefore needs to be recalculated..
	do i=1,extot
	ix=iexpos(1,i)
	iy=iexpos(2,i)
	iz=iexpos(3,i)
	j=iab1(ix,iy,iz)
	icume(j)=i
	iab1(ix,iy,iz)=iab1(ix,iy,iz)+1
	end do
c
c
c reset iab1 for use in inner loop
	do i=1,extot
	ix=iexpos(1,i)
	iy=iexpos(2,i)
	iz=iexpos(3,i)
	iab1(ix,iy,iz)=iab1(ix,iy,iz)-1
	end do

c
c
c icume now contains pointers to each dot inside a particular box
c and each box has 2 pointers into icume.,a start pointer and a finish
c pointer
c use however you want...
c
	i_iexpos= memalloc(i_iexpos,0)
c
	return
	end
