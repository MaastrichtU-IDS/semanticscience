	subroutine msrf(natom,igrid,xn1,scale,radprb,oldmid,extot,ibnum 
     &  ,egrid,nobject,numbmol,ibnumsurf)
	include 'pointer.h'
c-----------------------------------------------------------------------
	integer itot, vindx(1), vtot,nobject
	real vert(3,1), vnorm(3,1), vnorm2(3,1)
	integer atndx(1)
	pointer (i_vnorm2,vnorm2)
c-----------------------------------------------------------------------
c	parameter (mxvtx=200000, mxtri=400000)
	integer realsiz, intsiz
	parameter(realsiz=4)
	parameter (intsiz=4)
	character*5 fixyn
	real xo(3),xo2(3)
	integer isrfin(1)
	logical fix
c
c	hole-fixing variables
c	integer vtlen(mxvtx)
c	integer  vtlst(6*mxvtx), tmlst(9, mxtri), vtpnt(mxvtx)
	integer vtlen(1)
	integer  vtlst(1),tmlst(1),vtpnt(1)
c	end of hole-fixing variables
        integer iepsmp(igrid,igrid,igrid,3)
c b+++++++++++++++++++++++++
        integer numbmol,epsdim
c e+++++++++++++++++++++++++
        integer egrid(igrid,igrid,igrid,3)
	real oldmid(3),v1(3),v2(3),v3(3)
	real xn1(3,natom),rad3(natom),atsurf(1)
	logical out,nbe(0:6),exists
c
	mxvtx=ibnum*2.2
	mxtri=2*mxvtx
        epsdim=natom+nobject+2
        do k=1,igrid
        do j=1,igrid
        do i=1,igrid
c b+++++++++++++++++++++++++++++++++++++
c cambiato da mod a div, mi dovrebbe servire solo il mezzo
        egrid(i,j,k,1)=iepsmp(i,j,k,1)/epsdim
        egrid(i,j,k,2)=iepsmp(i,j,k,2)/epsdim
        egrid(i,j,k,3)=iepsmp(i,j,k,3)/epsdim
c e+++++++++++++++++++++++++++++++++++++
        end do
        end do
        end do
        do i = 1, igrid
          do j = 1, igrid
            egrid(i,1,j,1) = egrid(i,1,j,2)
            egrid(i,j,1,1) = egrid(i,j,1,3)
           end do
        end do
          do k = 2, igrid
         do j = 2, igrid
        do i = 2, igrid
            iate = 0
            if (egrid(i,j,k,1) .gt. 0) iate = iate + 1
            if (egrid(i,j,k,2) .gt. 0) iate = iate + 1
            if (egrid(i,j,k,3) .gt. 0) iate = iate + 1
            if (egrid(i-1,j,k,1) .gt. 0) iate = iate + 1
            if (egrid(i,j-1,k,2) .gt. 0) iate = iate + 1
            if (egrid(i,j,k-1,3) .gt. 0) iate = iate + 1
            if (iate  .le. 3) then
                egrid(i,j,k,1) = 0
            else
                egrid(i,j,k,1) = 1
            end if
          end do
         end do
        end do

123 	continue

	i_vindx = memalloc(i_vindx,3*mxtri*intsiz)
	i_vert = memalloc(i_vert,3*mxvtx*realsiz)

	call ex(igrid,egrid, vtot, itot, vindx, vert, "./", 2 )
	if(vtot.gt.mxvtx)then
	write(6,*)'vtot = ',vtot,' > mxvtx = ',mxvtx
	write(6,*)'increase mxvtx in msrf.f'
	stop
	endif

	do ib=1,vtot
	vert(1,ib)=vert(1,ib)/2.
	vert(2,ib)=vert(2,ib)/2.
	vert(3,ib)=vert(3,ib)/2.
	end do
c
	itot = itot/3
c scale boundary grid point positions relative to acc data
	write(6,*)'scaling vertices'
	i_vnorm = memalloc(i_vnorm,3*vtot*realsiz)
	i_vnorm2=0
	i_vnorm2 = memalloc(i_vnorm2,3*vtot*realsiz)
        call ddtime(tary)
        call sclbp(natom,igrid,xn1,scale,radprb,oldmid,vtot,
     &  extot,iall,vert,vnorm,nobject,numbmol,ibnumsurf)

c fix holes and make vertex to triangle arrays
c allocate hole-fixing arrays next
c hole-fixing variables

	if (vtot .lt. mxvtx/2) then
	    imxvtx = vtot*2
	else
	    imxvtx = mxvtx
	end if

	if (itot .lt. mxtri/2) then
	    imxtri = itot*2
	else
	    imxtri = mxtri
	end if
	
	i_vtlen = memalloc(i_vtlen,4*imxvtx)
	i_vtlst = memalloc(i_vtlst,6*imxvtx*intsiz)
	i_tmlst = memalloc(i_tmlst,9*imxtri*intsiz)
	i_vtpnt = memalloc(i_vtpnt,imxvtx*intsiz)

        call mkvtl(1,vtot, 1,itot, vtpnt, vtlen, vindx,
     $      vtlst, tmlst, imxtri, imxvtx)
        call fxhl(1,vtot,1,itot,ntot, vtpnt,
     $      vtlen, vindx, itot, vtlst, vert, vtot,
     $      tmlst, imxvtx, imxtri, vnorm)

        call fxhl(1,vtot,1,itot,ntot2, vtpnt,
     $      vtlen, vindx, itot, vtlst, vert, vtot,
     $      tmlst, imxvtx, imxtri, vnorm)

c	write(*,*) "number of triangles added to fix holes= ",ntot+ntot2

	if (ntot2 .gt. 0)  then
	    fix = .true.
	else
	    fix = .false.
	endif

	do while ( fix)
            call fxhl(1,vtot,1,itot,ntot2, vtpnt,
     $          vtlen, vindx, itot, vtlst, vert, vtot,
     $          tmlst, imxvtx, imxtri, vnorm)
c	    write(*,*) "number of triangles added to fix holes= ",ntot2
	    if (ntot2 .gt. 0) then
		fix = .true.
	    else
		fix = .false.
	    endif
	end do
	if(itot.gt.mxtri)then
	write(6,*)'itot = ',itot,' > mxtri = ',mxtri
	write(6,*)'increase mxtri in msrf.f'
	stop
	endif
	i_vtemp = memalloc(i_vtemp,0)

	i_vtlen=memalloc(i_vtlen,0)
	i_vtlst=memalloc(i_vtlst,0)
	i_tmlst=memalloc(i_tmlst,0)
	i_vtpnt=memalloc(i_vtpnt,0)

	write(6,*) 'number of vertices = ',vtot
	write(6,*) 'number of triangles = ',itot

	do i=1,vtot
	vnorm2(1,i)=0.0
	vnorm2(2,i)=0.0
	vnorm2(3,i)=0.0
	end do
c calculate area
	area=0.0
	areas=0.0
	areac=0.0
	arear=0.0
c	write(2,*)'LINE'
	do it=1,itot
	iv1=vindx(3*it-2)
	iv2=vindx(3*it-1)
	iv3=vindx(3*it)
c write out triangle
c	write(2,'(3f10.4,a2)')vert(1,iv1),vert(2,iv1),vert(3,iv1),' P'
c	write(2,'(3f10.4,a2)')vert(1,iv2),vert(2,iv2),vert(3,iv2),' L'
c	write(2,'(3f10.4,a2)')vert(1,iv3),vert(2,iv3),vert(3,iv3),' L'
	do k=1,3
	v1(k)=vert(k,iv2)-vert(k,iv1)
	v2(k)=vert(k,iv3)-vert(k,iv1)
	end do
	vx=v1(2)*v2(3)-v1(3)*v2(2)
	vy=v1(3)*v2(1)-v1(1)*v2(3)
	vz=v1(1)*v2(2)-v1(2)*v2(1)
	vmg=sqrt(vx*vx+vy*vy+vz*vz)
	tar=vmg/2.
	vx=vnorm(1,iv1)+vnorm(1,iv2)+vnorm(1,iv3)
	vy=vnorm(2,iv1)+vnorm(2,iv2)+vnorm(2,iv3)
	vz=vnorm(3,iv1)+vnorm(3,iv2)+vnorm(3,iv3)
	vmg=sqrt(vx*vx+vy*vy+vz*vz)
	vnorm2(1,iv1)=vnorm2(1,iv1)+vx/vmg
	vnorm2(2,iv1)=vnorm2(2,iv1)+vy/vmg
	vnorm2(3,iv1)=vnorm2(3,iv1)+vz/vmg
	vnorm2(1,iv2)=vnorm2(1,iv2)+vx/vmg
	vnorm2(2,iv2)=vnorm2(2,iv2)+vy/vmg
	vnorm2(3,iv2)=vnorm2(3,iv2)+vz/vmg
	vnorm2(1,iv3)=vnorm2(1,iv3)+vx/vmg
	vnorm2(2,iv3)=vnorm2(2,iv3)+vy/vmg
	vnorm2(3,iv3)=vnorm2(3,iv3)+vz/vmg
c calculate spherical triangle area if appropriate
	ia1=atndx(iv1)
	ia2=atndx(iv2)
	ia3=atndx(iv3)
	if(ia1.gt.0)then
	if(ia1.eq.ia2.and.ia1.eq.ia3)then
	rad=rad3(ia1)
	rad2=rad*rad
	aa=0.0
	bb=0.0
	cc=0.0
	do k=1,3
	aa=aa+(vert(k,iv2)-vert(k,iv1))**2
	bb=bb+(vert(k,iv3)-vert(k,iv2))**2
	cc=cc+(vert(k,iv1)-vert(k,iv3))**2
	end do
	aa=acos(1.-aa/(2.*rad2))
	bb=acos(1.-bb/(2.*rad2))
	cc=acos(1.-cc/(2.*rad2))
	ss=(aa+bb+cc)*.5
	tne4=sqrt(tan(ss*.5)*tan((ss-aa)*.5)*tan((ss-bb)*.5)*tan((ss-cc)
     &  *.5))
	tar=4.*atan(tne4)*rad2
	endif
	endif
	area=area+tar

	end do
	
	do i=1,vtot
	xn=vnorm2(1,i)
	yn=vnorm2(2,i)
	zn=vnorm2(3,i)
	vmg=sqrt(xn*xn+yn*yn+zn*zn)
	vnorm2(1,i)=vnorm2(1,i)/vmg
	vnorm2(2,i)=vnorm2(2,i)/vmg
	vnorm2(3,i)=vnorm2(3,i)/vmg
	end do

	write(6,*)'MS area                = ',area

	call wrtsurf("grasp.srf",9, oldmid, vert,
     $	vtot, vindx, itot, vnorm)

c	call wrtspdb("test.surf",9,vtot, vert)
	return
	end
