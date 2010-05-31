	subroutine ex(igrid,egrid,ivn,iv,ivert,vc,vdat1,lvdat1)
c
        parameter (mxtri=200000)
        parameter (mxvtx=100000)
c
 	integer egrid(igrid,igrid,igrid), e2(257,257,2)
c	integer ivert(150000),ipv(5,129,129)
c	dimension vc(3,100000)
	integer ivert(1),ipv(5,257,257)
	real vc(3,1)
	integer itind(0:256),itrn(2208),ivslb(3,32000)
      	character*20 uplbl
      	character*10 nxtlbl
      	character*60 toplbl
      	character*16 botlbl
      	character*80 vdat1,vdat2
      	real*4 oldmid(3)
c
c	vdat2(:lvdat1+1)=vdat1(:lvdat1+1)
c	vdat2(lvdat1+2:lvdat1+7)="v3.dat"

c
	fourth=1.0/4.0
	tnow=cputime(0.)
c	open(11,file=vdat2(:lvdat1+7),form="unformatted")
	open(11,file="/usr/local/bin/v3.dat",
     &	form="unformatted")
	read(11)itind,itrn
	close(11)
c
c loop for times
c
	do iy=1,igrid
	    do ix=1,igrid
		ipv(1,ix,iy)=0
		ipv(2,ix,iy)=0
		ipv(3,ix,iy)=0
		ipv(4,ix,iy)=0
		ipv(5,ix,iy)=0
	    end do
	end do
c
	do iy=1,igrid
	    do ix=1,igrid
		if(egrid(ix,iy,1).le.0) then
		    e2(ix,iy,2)=0
		else
		    e2(ix,iy,2)=1
		end if
	    end do
	end do
c
	ibox=0
	iv=0
	ivn=0
	do iz=1,igrid-1
c
	do iy=1,igrid
	    do ix=1,igrid
		e2(ix,iy,1)=e2(ix,iy,2)
		if(egrid(ix,iy,iz+1).le.0) then
		e2(ix,iy,2)=0
		else
		e2(ix,iy,2)=1
		end if
	    end do
	end do
c
	k=0
	do iy=1,igrid-1
	j=e2(1,iy,1)+e2(1,iy+1,1)+e2(1,iy+1,2)+e2(1,iy,2)
	do ix=1,igrid-1
c
	i2=e2(ix+1,iy,1) +
     & 	e2(ix+1,iy+1,1)+
     & 	  e2(ix+1,iy+1,2) +
     &    	  e2(ix+1,iy,2)
	i=i2+j
	j=i2
c
	if((i.ne.0).and.(i.ne.8)) then
	    k=k+1
c
c determine index of box, 1,254
c it was found to be better to calculate the index NOW, not later
c
	    indx=e2(ix,iy,1)+2*e2(ix,iy+1,1) +
     &  4*e2(ix+1,iy+1,1)+8*e2(ix+1,iy,1)+
     &  16*e2(ix,iy,2)+32*e2(ix,iy+1,2)+
     &  64*e2(ix+1,iy+1,2)+128*e2(ix+1,iy,2)
	ivslb(1,k)=ix
	ivslb(2,k)=iy
	ivslb(3,k)=indx
	end if
c loop over those verticies in the triangle list for this index
c
c loop to next box
	end do
	end do
c
	z2=float(2*iz)
	do i=1,k
	ix=ivslb(1,i)
	iy=ivslb(2,i)
	indx=ivslb(3,i)
c
	x2=float(2*ix)
	y2=float(2*iy)
	do i1=itind(indx),itind(indx+1)-1
	iv=iv+1
	n=itrn(i1)
c
c for each vertex, if it has a number in the vertex slab use it
c if not, increment the new vertex counter anf fill ivc with the
c right coordinaates
c
	goto(10,20,30,40,50,60,70,80,90,100,110,120) n
10	j=ipv(3,ix,iy)
	if(j.ne.0) then
		ivert(iv)=j
	else
	    ivn=ivn+1
	    ipv(3,ix,iy)=ivn
	    ivert(iv)=ivn
	    vc(1,ivn)=x2
	    vc(2,ivn)=y2
	    vc(3,ivn)=z2+1
	end if
	goto 200
c
20	j=ipv(5,ix,iy)
	if(j.ne.0) then
	    ivert(iv)=j
	else
	    ivn=ivn+1
	    ipv(5,ix,iy)=ivn
	    ivert(iv)=ivn
	    vc(1,ivn)=x2
	    vc(2,ivn)=y2+1
	    vc(3,ivn)=z2+2
	end if
	goto 200
c
30	j=ipv(3,ix,iy+1)
	if(j.ne.0) then
	    ivert(iv)=j
	else
	    ivn=ivn+1
	    ipv(3,ix,iy+1)=ivn
	    ivert(iv)=ivn
	    vc(1,ivn)=x2
	    vc(2,ivn)=y2+2
	    vc(3,ivn)=z2+1
	end if
	goto 200
c
40	j=ipv(2,ix,iy)
	if(j.ne.0) then
	ivert(iv)=j
	else
	ivn=ivn+1
	ipv(2,ix,iy)=ivn
	ivert(iv)=ivn
	vc(1,ivn)=x2
	vc(2,ivn)=y2+1
	vc(3,ivn)=z2
	end if
	goto 200
c
50	j=ipv(1,ix,iy)
	if(j.ne.0) then
	ivert(iv)=j
	else
	ivn=ivn+1
	ipv(1,ix,iy)=ivn
	ivert(iv)=ivn
	vc(1,ivn)=x2+1
	vc(2,ivn)=y2
	vc(3,ivn)=z2
	end if
	goto 200
c
60	j=ipv(4,ix,iy)
	if(j.ne.0) then
	ivert(iv)=j
	else
	ivn=ivn+1
	ipv(4,ix,iy)=ivn
	ivert(iv)=ivn
	vc(1,ivn)=x2+1
	vc(2,ivn)=y2
	vc(3,ivn)=z2+2
	end if
	goto 200
c
70	j=ipv(4,ix,iy+1)
	if(j.ne.0) then
	ivert(iv)=j
	else
	ivn=ivn+1
	ipv(4,ix,iy+1)=ivn
	ivert(iv)=ivn
	vc(1,ivn)=x2+1
	vc(2,ivn)=y2+2
	vc(3,ivn)=z2+2
	end if
	goto 200
c
80	j=ipv(1,ix,iy+1)
	if(j.ne.0) then
	ivert(iv)=j
	else
	ivn=ivn+1
	ipv(1,ix,iy+1)=ivn
	ivert(iv)=ivn
	vc(1,ivn)=x2+1
	vc(2,ivn)=y2+2
	vc(3,ivn)=z2
	end if
	goto 200
c
90	j=ipv(3,ix+1,iy)
	if(j.ne.0) then
	ivert(iv)=j
	else
	ivn=ivn+1
	ipv(3,ix+1,iy)=ivn
	ivert(iv)=ivn
	vc(1,ivn)=x2+2
	vc(2,ivn)=y2
	vc(3,ivn)=z2+1
	end if
	goto 200
c
100	j=ipv(5,ix+1,iy)
	if(j.ne.0) then
	ivert(iv)=j
	else
	ivn=ivn+1
	ipv(5,ix+1,iy)=ivn
	ivert(iv)=ivn
	vc(1,ivn)=x2+2
	vc(2,ivn)=y2+1
	vc(3,ivn)=z2+2
	end if
	goto 200
c
110	j=ipv(3,ix+1,iy+1)
	if(j.ne.0) then
	ivert(iv)=j
	else
	ivn=ivn+1
	ipv(3,ix+1,iy+1)=ivn
	ivert(iv)=ivn
	vc(1,ivn)=x2+2
	vc(2,ivn)=y2+2
	vc(3,ivn)=z2+1
	end if
	goto 200
c
120	j=ipv(2,ix+1,iy)
	if(j.ne.0) then
	ivert(iv)=j
	else
	ivn=ivn+1
	ipv(2,ix+1,iy)=ivn
	ivert(iv)=ivn
	vc(1,ivn)=x2+2
	vc(2,ivn)=y2+1
	vc(3,ivn)=z2
	end if
c
200	continue
	end do
	end do
c
	do i=1,k
	ix=ivslb(1,i)
	iy=ivslb(2,i)
	ipv(3,ix,iy)=0
	ipv(1,ix,iy)=ipv(4,ix,iy)
	ipv(2,ix,iy)=ipv(5,ix,iy)
	ipv(4,ix,iy)=0
	ipv(5,ix,iy)=0
	end do
c
	end do
c
c it loop for timing
	snow= cputime(tnow)
c	write(6,*) "number of vertices= ",ivn
c	write(6,*) "number of triangles = ",iv/3
	return
	end
