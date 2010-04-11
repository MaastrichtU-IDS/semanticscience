	subroutine fxhl(ivbeg,ivend,itbeg,itend,ntot, vtpnt,
     &	vtlen, vindx, itot, vtlst, vert, vtot, tmlst,imxvtx, imxtr
     &  i, vnor)

	implicit none

	integer mxvtx, mxtri, intsiz
	parameter (mxvtx=150000, mxtri=300000)
	integer itbeg, itend, ivbeg, ivend, ntot, imxvtx, imxtri
	integer vtlen(imxvtx)
	integer vtpnt(imxvtx), vtlst(6*imxvtx), vtot, itot
	integer vindx(3*mxtri), tmlst(9, imxtri)
	real vert(3, vtot), vnor(3,vtot)
	
	integer is, ir, i, j1, j2, j3, i1, i2, n, it, id, nsel(mxvtx),
     &	tv(20),vl(100)
	real a1,b1, c1, a2, b2, c2, disnor, xnor, ynor, znor, p1, p2, p3
	integer j,k,n1

	ntot=itot

	do i=ivbeg,ivend
	    nsel(i)=0
	end do

	is=0
	ir=0
	do i=ivbeg,ivend
	    i1=vtpnt(i)
	    i2=i1+vtlen(i)-1

	    n=0
	    do j=i1,i2
		k=3*vtlst(j)
		j1=vindx(k-2)
		j2=vindx(k-1)
		j3=vindx(k)
		if(j1.gt.i)then
		    nsel(j1)=nsel(j1)+1
		    n=n+1
		    vl(n)=j1
		end if
		if(j2.gt.i)then
		    nsel(j2)=nsel(j2)+1
		    n=n+1
		    vl(n)=j2
		end if
		if(j3.gt.i)then
		    nsel(j3)=nsel(j3)+1
		    n=n+1
		    vl(n)=j3
		end if
c k= one of the triangles
	    end do

	    it=0
	    do j=1,n
		k=vl(j)
		if((nsel(k).ne.0).and.(nsel(k).ne.2)) then
		    it=it+1
		    tv(it)=k
		end if
		nsel(k)=0
	    end do

	    if(it.gt.0) is=is+1

c mend
	    if(it.eq.2) then
		n1=tv(1)
		id=1
		do j=i1,i2
		    k=3*vtlst(j)
		    j1=vindx(k-2)
		    j2=vindx(k-1)
		    j3=vindx(k)
		    if(j1.eq.n1) id=1
		    if(j3.eq.n1) id=2
		    if(j2.eq.n1) then
			if(j1.eq.i) id=2
		    else
			if(j3.eq.i) id=1
		    end if
		end do
	
		j1=i
		j2=tv(1)
		j3=tv(2)

		a1=vert(1,j2) - vert(1,j1)
		b1=vert(2,j2) - vert(2,j1)
		c1=vert(3,j2)-vert(3,j1)

		a2=vert(1,j3)-vert(1,j1)
		b2=vert(2,j3)-vert(2,j1)
		c2=vert(3,j3)-vert(3,j1)

		xnor=c2*b1-c1*b2
		ynor=a2*c1-a1*c2
		znor=a1*b2-a2*b1

		disnor=sqrt(xnor**2+ynor**2+znor**2)
		xnor=xnor/disnor
		ynor=ynor/disnor
		znor=znor/disnor

		p1=xnor*vnor(1,j1)+ynor*vnor(2,j1)+znor*vnor(3,j1)
		p2=xnor*vnor(1,j2)+ynor*vnor(2,j2)+znor*vnor(3,j2)
		p3=xnor*vnor(1,j3)+ynor*vnor(2,j3)+znor*vnor(3,j3)

		if((p1.lt.0).and.(p2.lt.0).and.(p3.lt.0)) then
		    id=2
		else
		    id=1
		end if

		itot=itot+1
		if(id.eq.1) then
		    vindx(3*itot-2)=i
		    vindx(3*itot-1)=tv(1)
		    vindx(3*itot)=tv(2)
		end if
		if(id.eq.2) then
		    vindx(3*itot-2)=tv(2)
		    vindx(3*itot-1)=tv(1)
		    vindx(3*itot)=i
		end if

		ir=ir+1
	    end if

	end do

	ntot=itot-ntot

c remake vertex to triangles listing..
	call mkvtl(ivbeg,ivend,itbeg,itot, vtpnt, vtlen, vindx,
     $	vtlst, tmlst, imxtri, imxvtx)

	return
	end
