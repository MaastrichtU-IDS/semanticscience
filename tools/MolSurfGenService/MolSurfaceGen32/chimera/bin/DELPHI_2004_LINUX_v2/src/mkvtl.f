	subroutine mkvtl(ivbeg,ivend,itbeg,itend, vtpnt, vtlen, vindx,
     &	vtlst, tmlst, imxtri, imxvtx)
c
c	implicit none
	integer mxvtx, mxtri, intsiz, itbeg, itend, ivbeg, ivend
	integer imxvtx, imxtri
	integer vtlen(imxvtx)
	integer vindx(3*imxtri), vtlst(6*imxvtx), tmlst(9, imxtri),
     &	vtpnt(imxvtx)

	parameter(mxtri=300000)
	integer vtemp(mxtri), i, j1, j2, j3, k1, k2, k3
	integer im, it1, it2, j
	real tarray1(2),tarray2(2), t1

c        write(6,*) "starting.."
	do i=ivbeg,ivend
	    vtlen(i)=0
	end do

	do i=itbeg,itend
	    j1=vindx(3*i-2)
	    j2=vindx(3*i-1)
	    j3=vindx(3*i)
	    vtlen(j1)=vtlen(j1)+1
	    vtlen(j2)=vtlen(j2)+1
	    vtlen(j3)=vtlen(j3)+1
	end do

	if(ivbeg.ne.1) vtpnt(ivbeg)=vtpnt(ivbeg-1)+vtlen(ivbeg-1)
	if(ivbeg.eq.1) vtpnt(ivbeg)=1

	do i=ivbeg+1,ivend
	    vtpnt(i)=vtpnt(i-1)+vtlen(i-1)
	end do
	vtpnt(ivend+1)=vtpnt(ivend)+vtlen(ivend)

	do i=ivbeg,ivend
	    vtlen(i)=0
	end do
c
	do i=itbeg,itend
	    j1=vindx(3*i-2)
	    j2=vindx(3*i-1)
	    j3=vindx(3*i)
	    k1=vtpnt(j1)+vtlen(j1)
	    k2=vtpnt(j2)+vtlen(j2)
	    k3=vtpnt(j3)+vtlen(j3)
	    vtlen(j1)=vtlen(j1)+1
	    vtlen(j2)=vtlen(j2)+1
	    vtlen(j3)=vtlen(j3)+1
	    vtlst(k1)=i
	    vtlst(k2)=i
	    vtlst(k3)=i
	end do
c
ct1=eetime(tarray1)
c
	do i=itbeg,itend
	    vtemp(i)=0
	end do
c
	im=0
	do i=itbeg,itend
c
	    j1=vindx(3*i-2)
	    j2=vindx(3*i-1)
	    j3=vindx(3*i)
c
c which triangle borders edge j1-j2
	    do j=vtpnt(j1),vtpnt(j1)+vtlen(j1)-1
		k1=vtlst(j)
		vtemp(k1)=j1
	    end do
	    it1=0
	    do j=vtpnt(j2),vtpnt(j2)+vtlen(j2)-1
		k1=vtlst(j)
		if((vtemp(k1).eq.j1).and.(k1.ne.i)) it1=k1
		vtemp(k1)=j2
	    end do
c which point completes the triangle
	    it2=0
	    if(it1.ne.0) then
		k1=vindx(3*it1-2)
		k2=vindx(3*it1-1)
		k3=vindx(3*it1)
		if((k1.ne.j1).and.(k1.ne.j2)) it2=k1
		if((k2.ne.j1).and.(k2.ne.j2)) it2=k2
		if((k3.ne.j1).and.(k3.ne.j2)) it2=k3
	    end if
c fill tmlst
	    tmlst(1,i)=it1
	    tmlst(4,i)=it2
	    tmlst(7,i)=j3
	    im=im+it1
c
c which triangle borders edge j2-j3
	    it1=0
	    do j=vtpnt(j3),vtpnt(j3)+vtlen(j3)-1
		k1=vtlst(j)
		if((vtemp(k1).eq.j2).and.(k1.ne.i)) it1=k1
		vtemp(k1)=j3
	    end do
c which point completes the triangle
	    it2=0
	    if(it1.ne.0) then
		k1=vindx(3*it1-2)
		k2=vindx(3*it1-1)
		k3=vindx(3*it1)
		if((k1.ne.j2).and.(k1.ne.j3)) it2=k1
		if((k2.ne.j2).and.(k2.ne.j3)) it2=k2
		if((k3.ne.j2).and.(k3.ne.j3)) it2=k3
	    end if
c fill tmlst
	    tmlst(2,i)=it1
	    tmlst(5,i)=it2
	    tmlst(8,i)=j1
	    im=im+it1
c
c which triangle borders edge j3-j1
	    it1=0
	    do j=vtpnt(j1),vtpnt(j1)+vtlen(j1)-1
		k1=vtlst(j)
		if((vtemp(k1).eq.j3).and.(k1.ne.i)) it1=k1
	    end do
c which point completes the triangle
	    it2=0
	    if(it1.ne.0) then
		k1=vindx(3*it1-2)
		k2=vindx(3*it1-1)
		k3=vindx(3*it1)
		if((k1.ne.j3).and.(k1.ne.j1)) it2=k1
		if((k2.ne.j3).and.(k2.ne.j1)) it2=k2
		if((k3.ne.j3).and.(k3.ne.j1)) it2=k3
	    end if
c fill tmlst
	    tmlst(3,i)=it1
	    tmlst(6,i)=it2
	    tmlst(9,i)=j2
	    im=im+it1
c
	end do
c
ct2=eetime(tarray2)
c	write(6,*) "finishing",t2-t1,im
c
	return
	end
