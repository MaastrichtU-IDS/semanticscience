C program to expand the vw surface into Richards' molecular surface
c (S. Sridharan		May 1994)
	subroutine vwtms(ibnum,xn1,natom,oldmid,limeps,ionlymol,nmedia
     &  ,nobject,ibmx,numbmol)
	include 'acc2.h'
	include 'qlog.h'
	integer cbn1(1),cbn2(1),cbal(1)
	integer iab1(1),iab2(1),icume(1)
	logical outcb(-2:2,-2:2,-2:2)
	character*80 line
	integer nbra(1000)
        pointer (i_egrid,egrid)
        integer egrid(1)
c
c subroutine to take a van der Waals epsmap and expand it into a
c molecular volume map..
c procedure is to first generate a list of accessible points
c whose collective volume may contain any midpoint in the box.
c next send these points to be mapped into indexing arrays...
c then take the vanderwaals epsmap and grow it out to the molecular
c epsmap, checking against the set of accessible points..
c
c can't do the vw surface by projecting midpoints to accessible surface and
c testing if that point is in or outside the accessible volume (20 Oct 92)
c (but can do the contact part of MS that way, Nov 93)
c
c       integer ibnd(3*ibmx)
        integer ibnd(1)
	integer ibgrd(1),limeps(2,3),atsurf(1)
c b+++++++++++++
	integer bndeps(igrid,igrid,igrid,2),eps(6),nt,remov,
     &	iepsmp(igrid,igrid,igrid,3),ibnumsurf,itmp(6),numbmol,dim1
        integer iaprec,objecttype,imap(4,6),dim,sign,epsdim,isign
        integer nmedia,nobject,iatmmed(natom+nobject),cont
        integer kind,eps2(6)
        real itemp(3),rtemp(3)
        real limobject(nobject,3,2),xq(3),radpmax,zeta,axdist
        real tmp(6),tmp1,dx,dy,dz,dist,prbrd12,prbrd22
        character*80 dataobject(nobject,2)
        character*80 strtmp
        logical debug,ionlymol
c e+++++++++++++
	real goff(3,6),xg(3),oldmid(3),scspos(1)
	real xn1(3,natom),xn2(3,natom),rad3(natom)
	logical out,nbe(0:6),intb,exists
      
	  debug=.false.
        i_ibnd= memalloc(i_ibnd,4*3*ibmx)
	i_r0= memalloc(i_r0,4*natom)
	i_r02= memalloc(i_r02,4*natom)
	i_rs2= memalloc(i_rs2,4*natom)
	i_ast= memalloc(i_ast,4*natom)

c b+++++++++++++++++++++++++++++++
        epsdim=natom+nobject+2
c imap maps from midpoint position to iepsmap entry positions
        do j=1,6
           do i=1,3
             imap(i,j)=0
           end do
        end do
        imap(1,4)=-1
        imap(2,5)=-1
        imap(3,6)=-1
        imap(4,1)=1
        imap(4,2)=2
        imap(4,3)=3
        imap(4,4)=1
        imap(4,5)=2
        imap(4,6)=3
c e++++++++++++++++++++++++++++++++++++++++++++++
	do k=-2,2
	do j=-2,2
	do i=-2,2
	outcb(i,j,k)=.true.
	end do
	end do
	end do
	do k=-1,1
	do j=-1,1
	do i=-1,1
	outcb(i,j,k)=.false.
	end do
	end do
	end do

	nbe(0)=.false.
	nbe(6)=.false.
	nbe(1)=.true.
	nbe(2)=.true.
	nbe(3)=.true.
	nbe(4)=.true.
	nbe(5)=.true.
c
	off=0.5/scale
	do i=1,6
	do j=1,3
	goff(j,i)=0.0
	end do
	end do
	goff(1,1)=off
	goff(2,2)=off
	goff(3,3)=off
	goff(1,4)=-off
	goff(2,5)=-off
	goff(3,6)=-off

c b++++++++++++++++++++++++++++++++
        radpmax=max(radprb(1),radprb(2))
c e+++++++++++++++++++++++++++++++++
c
c convertion from grid to real coordinates(can also use routine gtoc)
	x1=1.0/scale
	x1x=oldmid(1)-(1.0/scale)*float(igrid+1)*0.5
	x1y=oldmid(2)-(1.0/scale)*float(igrid+1)*0.5
	x1z=oldmid(3)-(1.0/scale)*float(igrid+1)*0.5
c find extrema
c b++++++++++++++++++++
c find global extrema
        cmin(1)=6000
        cmin(2)=6000
        cmin(3)=6000
        cmax(1)=-6000
        cmax(2)=-6000
        cmax(3)=-6000
        do ii=1,nobject
        cmin(1)=min(cmin(1),limobject(ii,1,1))
        cmin(2)=min(cmin(2),limobject(ii,2,1))
        cmin(3)=min(cmin(3),limobject(ii,3,1))
        cmax(1)=max(cmax(1),limobject(ii,1,2))
        cmax(2)=max(cmax(2),limobject(ii,2,2))
        cmax(3)=max(cmax(3),limobject(ii,3,2))
        end do
c e+++++++++++++++++++

c       rdmx=0.0
c       do 2103 ix=1,natom
c       cmin(1)=min(cmin(1),xn1(1,ix))
c       cmin(2)=min(cmin(2),xn1(2,ix))
c       cmin(3)=min(cmin(3),xn1(3,ix))
c       cmax(1)=max(cmax(1),xn1(1,ix))
c       cmax(2)=max(cmax(2),xn1(2,ix))
c       cmax(3)=max(cmax(3),xn1(3,ix))
c       rdmx=max(rdmx,rad3(ix))
c2103	continue

c find vanderwaals boundary
	n=0
        nn=0
	nmt=0
	nmmt=0

c NB change limits to those of the molecule.
c set for iepsmp NOT equal to unity
	do k=limeps(1,3)+1,limeps(2,3)-1
	do j=limeps(1,2)+1,limeps(2,2)-1
	do i=limeps(1,1)+1,limeps(2,1)-1
c b+++++++++++++
c  one distinguishes between internal,external,
c internal bgp and external bgp
          iext=0
          ibgp=0

          itmp(1)=iabs(iepsmp(i,j,k,1))/epsdim
          itmp(2)=iabs(iepsmp(i,j,k,2))/epsdim
          itmp(3)=iabs(iepsmp(i,j,k,3))/epsdim
          itmp(4)=iabs(iepsmp(i-1,j,k,1))/epsdim
          itmp(5)=iabs(iepsmp(i,j-1,k,2))/epsdim
          itmp(6)=iabs(iepsmp(i,j,k-1,3))/epsdim
c         iaca=1
          if(itmp(1).eq.0) iext=1
          if(itmp(1).ne.itmp(6)) ibgp=1
c         if(itmp(1).eq.1) iaca=0
          do cont=2,6
            if(itmp(cont).eq.0) iext=1
            if(itmp(cont).ne.itmp(cont-1)) ibgp=1
c           if(itmp(cont).eq.1) iaca=0
          end do

c iaca da togliere
c         if (iaca.eq.1) ibgp=0
c assignement of right values to bndeps according to the 
c point nature
c from now ibnum is the total number of internal and external
c boundary grid points

          if (ibgp.gt.0) then
            n=n+1
            bndeps(i,j,k,1)=n
            bndeps(i,j,k,2)=iext
            if (iext.gt.0) nn=nn+1
            ibnd(3*n-2)=i
            ibnd(3*n-1)=j
            ibnd(3*n)=k
          else
            bndeps(i,j,k,1)=0
            bndeps(i,j,k,2)=0
          end if

c debugging++++++++++++++++++++++++++++++
          if (debug) then
            nt=0
c cambiato da mod a dim, dovrebbe servirmi il mezzo
            if((iepsmp(i,j,k,1)/epsdim).gt.0)nt=nt+1
            if((iepsmp(i,j,k,2)/epsdim).gt.0)nt=nt+1
            if((iepsmp(i,j,k,3)/epsdim).gt.0)nt=nt+1
            if((iepsmp(i-1,j,k,1)/epsdim).gt.0)nt=nt+1
            if((iepsmp(i,j-1,k,2)/epsdim).gt.0)nt=nt+1
            if((iepsmp(i,j,k-1,3)/epsdim).gt.0)nt=nt+1
            if (nbe(nt).neqv.((iext.eq.1).and.(ibgp.eq.1)))then
              write(6,*)'PROBLEMS1 ',i,j,k
              itemp(1)=i
              itemp(2)=j
              itemp(3)=k
              call gtoc(itemp,rtemp)
              write(6,*)rtemp
              write(6,*)iepsmp(i,j,k,1),iepsmp(i,j,k,2),iepsmp(i,j,k,3)
     &           ,iepsmp(i-1,j,k,1),iepsmp(i,j-1,k,2),iepsmp(i,j,k-1,3)
            end if
          end if
c debugging++++++++++++++++++++++++++++++
c e+++++++++++++
	end do
	end do
	end do
	ibnum=n
c b++++++++++
        ibnumsurf=nn
        nn=0
	write(6,*)'boundary points facing continuum solvent= ',ibnumsurf
c e++++++++++
        write(6,*)'total number of boundary points before elab.= ',ibnum
	if(ibnum.gt.ibmx)then
	  write(6,*)'ibnum= ',ibnum,' is greater than ibmx = ',ibmx
	  write(6,*)'increase ibmx in vwtms.f'
	  stop
	endif
c
c b+++++++++++++++++++++++++++++++
        if (.not.ionlymol.and.radprb(1).ne.radprb(2)) then
          do i=1,natom
            xq(1)=xn1(1,i)
            xq(2)=xn1(2,i)
            xq(3)=xn1(3,i)
            r0a=rad3(i)+radprb(1)
            do ii=1,nobject
              strtmp=dataobject(ii,1)
              read(strtmp(16:18),*)kind
              if (strtmp(1:4).ne.'is a'.and.kind.ne.2) then
                if( (xq(1)-rad3(i).lt.limobject(ii,1,2)).and.
     &              (xq(2)-rad3(i).lt.limobject(ii,2,2)).and.
     &              (xq(3)-rad3(i).lt.limobject(ii,3,2)).and.
     &              (xq(1)+rad3(i).gt.limobject(ii,1,1)).and.
     &              (xq(2)+rad3(i).gt.limobject(ii,2,1)).and.
     &              (xq(3)+rad3(i).gt.limobject(ii,3,1)) )then
                  call distobj(xq,dx,dy,dz,nobject,ii,0.,dist,
     &  .true.,zeta,axdist)
c only full buried atoms have the proberadius changed to radprb(2)
                  if (dist.lt.-rad3(i)) r0a=rad3(i)+radprb(2)
                end if
              end if
            end do
            r0(i)=r0a
            r02(i)=r0a*r0a
            rs2(i)=0.99999*r02(i)
          end do
        else
c e++++++++++++++++++++++++++++++
	  do i=1,natom
	    r0a=rad3(i)+radprb(1)
	    r0(i)=r0a
	    r02(i)=r0a*r0a
	    rs2(i)=0.99999*r02(i)
	  end do
        end if

        if(radpmax.lt.1.e-6) then
	  i_ibgrd= memalloc(i_ibgrd,4*3*ibnum)
	  do i=1,3*ibnum
	    ibgrd(i)=ibnd(i)
	  end do
	  do i=1,natom
	    ast(i)=0
	  end do
	  goto 222
	endif

        if(iacs) write(6,'(a21)') " opening surface file"
	if(iacs) open(40,file='hsurf2.dat')
c make a list of accessible points..,expos. all scaling of grid
c points will be done to thses points..
	prbrd12=radprb(1)*radprb(1)
        prbrd22=radprb(2)*radprb(2)

c calculate an identity for this conformation
	rsm=0.0
	do i=1,natom
	  rsm=rsm+rad3(i)*(abs(xn1(1,i))+abs(xn1(2,i))+abs(xn1(3,i)))
	end do
	inquire(file='ARCDAT',exist=exists)
	if(exists.and.ionlymol)then
	  open(1,file='ARCDAT',form='unformatted',status='old',err=999)
	  read(1)natm,radp,nacc,rsm1
c b++++++maybe it could be improved taking into account objects (Walter 1999)
	  if(natm.eq.natom.and.radp.eq.radprb(1).and.abs(rsm1-rsm).lt.
     &1.0e-8)then
c e++++++++++++++++++++++++++++++++++++++
	    write(6,*)'reading accessible surface arcs data from file
     &  ARCDAT'
	    extot=nacc
	    i_expos= memalloc(i_expos,4*3*extot)
	    call arcio(natm,extot,expos,ast,0)
            write(6,*)'no. of arc points read = ',nacc
            close (1)
            goto 111
          else
            close (1)
          endif
c temporaneo
c         extot=nacc
c         i_expos= memalloc(i_expos,4*3*extot)
c         call arcio(natm,extot,expos,0)
c         write(6,*)'no. of arc points read = ',nacc
c         close (1)
c         goto 111
        endif

        call ddtime(tary)
	call sas(xn1,natom,radprb,extot,nobject,numbmol,scale)
        call ddtime(tary)
        write(6,*)'mkacc time = ',tary(1)

	if(extot.gt.0.and.ionlymol)then
c maybe can be improved by taking into account objects
	  write(6,*)'writing accessible surface arcs data to  ARCDAT'
	  open(1,file='ARCDAT',form='unformatted',err=999)
	  write(1)natom,radprb(1),extot,rsm
c debug++++++++++++++++++++++++
c         open(52,file='expos',form='formatted')
c           do iiii=1,extot
c             write (52,*) expos(1,iiii),expos(2,iiii)
c            end do
c         close (52)
c end debug+++++++++++++++++++
             
c b+++++++++++++++++++++++++++++++++++++++++++
          if (natom.eq.0) then
	    call arcio1(extot,expos)
          else
            call arcio(natom,extot,expos,ast,1)
          end if
c e++++++++++++++++++++++++++++++++++++++++++
          close(1)
        endif
111	continue

	del=1./scale
	del=max(del,radpmax)
	cbln=rdmx+del
	call cubedata(2.0,cbln)
        dim=(lcb+1)*(mcb+1)*(ncb+1)
        i_cbn1= memalloc(i_cbn1,4*dim)
        i_cbn2= memalloc(i_cbn2,4*dim)
c b++++June2001+++++++++++++++++++++++
        dim1=27
        if ((nobject-numbmol).gt.0) dim1=max(dim,27)
c e+++++++++++++++++++++++++++++++++
        i_cbal= memalloc(i_cbal,4*dim1*(natom+nobject-numbmol))

	call cube(natom,xn1,rad3,nobject,numbmol,scale,radprb(1))
c 
	call ddtime(tary)
c
c link the accessible points into iab1 and iab2
	call indverdata(radpmax,scale)
	cba=1./grdi
        i_iab1= memalloc(i_iab1,4*(lcb1+1)*(mcb1+1)*(ncb1+1))
        i_iab2= memalloc(i_iab2,4*(lcb1+1)*(mcb1+1)*(ncb1+1))
        i_icume= memalloc(i_icume,4*extot)

	 write(6,*)'grid for indexing accessible points = ',cba
c         write(6,'(a22,3f8.3,3i6)')'mnx,mny,mnz,il,im,in: ',
c     &   mnx,mny,mnz,lcb1,mcb1,ncb1

	call indver(extot)
c write out surface data
        if(iacs) then
	  do i=1,extot
	    xg(1)=expos(1,i)
	    xg(2)=expos(2,i)
	    xg(3)=expos(3,i)
	    iv=1
	    call watput(i,iv,xo,line)
	    write(40,'(a80)') line
	  end do
	  close (40)
	end if
c now start the expansion
c m1= the number of boundary points removed from list
c
	ncav=0
c START
	n1=1
	n2=ibnum
c m= number of new boundary elements..
	mpr=100000
	ndv=0
100	m=0
	mr=0

	do i=n1,n2
	ix=ibnd(3*i-2)
	iy=ibnd(3*i-1)
	iz=ibnd(3*i)

c considering both internal and external b.g.p.
	if(bndeps(ix,iy,iz,1).ne.0) then
c still has to be considered what is external and what internal!!!!!WWW
c b++++++++++++++++++++++++++++++++++++
c remov is 1 if it is an internal midpoint close to an interface where a
c molecule is present (expansion has to take place also in objects)
        remov=0
c tengo il mod perche' deve prendere solo punti in atomi
	eps(1)=mod(iepsmp(ix,iy,iz,1),epsdim)
	eps(2)=mod(iepsmp(ix,iy,iz,2),epsdim)
        if((eps(1).gt.0.and.eps(1).le.natom+1).or.(eps(2).gt.0.and.
     &  eps(2).le.natom+1)) remov=1
	eps(3)=mod(iepsmp(ix,iy,iz,3),epsdim)
	eps(4)=mod(iepsmp(ix-1,iy,iz,1),epsdim)
        if((eps(3).gt.0.and.eps(3).le.natom+1).or.(eps(4).gt.0.and.
     &  eps(4).le.natom+1)) remov=1
	eps(5)=mod(iepsmp(ix,iy-1,iz,2),epsdim)
	eps(6)=mod(iepsmp(ix,iy,iz-1,3),epsdim)
        if((eps(5).gt.0.and.eps(5).le.natom+1).or.(eps(6).gt.0.and.
     &  eps(6).le.natom+1)) remov=1
c da farsi solo se pores eps2 contiene il mezzo
        eps2(1)=(iepsmp(ix,iy,iz,1)/epsdim)
        eps2(2)=(iepsmp(ix,iy,iz,2)/epsdim)
        eps2(3)=(iepsmp(ix,iy,iz,3)/epsdim)
        eps2(4)=(iepsmp(ix-1,iy,iz,1)/epsdim)
        eps2(5)=(iepsmp(ix,iy-1,iz,2)/epsdim)
        eps2(6)=(iepsmp(ix,iy,iz-1,3)/epsdim)

c e++++++++++++++++++++++++++++++++++++
c
	xg(1)=float(ix)*x1 +x1x
	xg(2)=float(iy)*x1 +x1y
	xg(3)=float(iz)*x1 +x1z
c
	do 200 j=1,6
c b++++++++++++++++++++++++++++
c       essere in poro ==> eps2=0 and eps >0
        if(eps(j).eq.0.or.(remov.eq.1.and.eps(j).gt.natom+1).or.
     &    (eps2(j).eq.0.and.eps(j).gt.0))then
          prbrd2=prbrd22
          if (eps(j).eq.0.or.eps2(j).eq.0) prbrd2=prbrd12
c e++++++++++++++++++++++++++++
c
c add midpoint offset to grid point..
	s1=xg(1)+goff(1,j)
	s2=xg(2)+goff(2,j)
	s3=xg(3)+goff(3,j)
c determine if this virgin midpoint is in or out
	xx=(s1-mnx)*grdi
	yy=(s2-mny)*grdi
	zz=(s3-mnz)*grdi
	jx=int(xx)
	jy=int(yy)
	jz=int(zz)

 	if(jx.le.0.or.jx.ge.lcb1.or.jy.le.0.or.jy.ge.mcb1.or.jz.le.0.
     &	or.jz.ge.ncb1) then
           write(6,*)'midpoint out of cube' 
           write(6,'(2i5,3f8.3,3i6)')i,j,xx,yy,zz,jx,jy,jz
           write(6,*)iepsmp(ix,iy,iz,1)
           write(6,*)iepsmp(ix,iy,iz,2)
           write(6,*)iepsmp(ix,iy,iz,3)
           write(6,*)iepsmp(ix-1,iy,iz,1)
           write(6,*)iepsmp(ix,iy-1,iz,2)
           write(6,*)iepsmp(ix,iy,iz-1,3)
        end if

	dmn=1000.
	iacv=0
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c -1,0,0
	jx=jx-1
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 1,0,0
	jx=jx+2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 0,-1,0
	jx=jx-1
	jy=jy-1
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 0,1,0
	jy=jy+2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 0,0,-1
	jy=jy-1
	jz=jz-1
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 0,0,1
	jz=jz+2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c nn=2
c 1,0,1
	jx=jx+1
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c -1,0,1
	jx=jx-2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 0,1,1
	jx=jx+1
	jy=jy+1
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 0,-1,1
	jy=jy-2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c -1,-1,0
	jz=jz-1
	jx=jx-1
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 1,-1,0
	jx=jx+2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 1,1,0
	jy=jy+2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c -1,1,0
	jx=jx-2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c -1,0,-1
	jz=jz-1
	jy=jy-1
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 1,0,-1
	jx=jx+2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 0,1,-1
	jx=jx-1
	jy=jy+1
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 0,-1,-1
	jy=jy-2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c nn=3
c -1,-1,-1
	jx=jx-1
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 1,-1,-1
	jx=jx+2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 1,1,-1
	jy=jy+2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c -1,1,-1
	jx=jx-2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c -1,1,1
	jz=jz+2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 1,1,1
	jx=jx+2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c 1,-1,1
	jy=jy-2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c -1,-1,1
	jx=jx-2
        liml=iab1(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
        limu=iab2(jx+1+(lcb1+1)*jy+(lcb1+1)*(mcb1+1)*jz)
	do ii=liml,limu
	iarv= icume(ii)
	dist=(s1-expos(1,iarv))**2 +(s2-expos(2,iarv))**2 +(s3-expos(3,i
     &  arv))**2
	if(dist.lt.prbrd2)then
	eps(j)=-1
        eps2(j)=-1
	goto 200
	elseif(dist.lt.dmn)then
	 iacv=iarv
	dmn=dist
	endif
	end do
c
c it might be in the contact region; find the closest atom surface
	it1=(s1-xo)*cbai
	it2=(s2-yo)*cbai
	it3=(s3-zo)*cbai
	dmn=100.
	iac=0
	nnbr=0
c b++++++++++++++++++++++++++++++++++++++
        if(it1.lt.0.or.it1.gt.lcb.or.it2.lt.0.or.it2.gt.mcb.or.it3.lt.
     &  0.or.it3.gt.ncb) then
c if the bgp is outside the cube, probably it is due to some object
          do ii=nobject,1,-1
            strtmp=dataobject(ii,1)
            read(strtmp(16:18),*)kind
            if (strtmp(1:4).ne.'is a'.and.kind.ne.2) then
            if ((s1.le.limobject(ii,1,2)+x1).and.(s1.gt.limobject(ii,1
     &  ,1)-x1))then
            if ((s2.le.limobject(ii,2,2)+x1).and.(s2.gt.limobject(ii,2
     &  ,1)-x1))then
            if ((s3.le.limobject(ii,3,2)+x1).and.(s3.gt.limobject(ii,3
     &  ,1)-x1))then
              nnbr=nnbr+1
              nbra(nnbr)=ii+natom
              liml=0
              limu=0
            endif
            endif
            endif
            endif
          end do
          if(liml.ne.0.or.limu.ne.0) write(6,*)'a bgp close to nothing'
        else
c e+++++++++++++++++++++++++++++++++++++++++
          liml=cbn1(it1+1+(lcb+1)*it2+(lcb+1)*(mcb+1)*it3)
          limu=cbn2(it1+1+(lcb+1)*it2+(lcb+1)*(mcb+1)*it3)
        endif

        iaprec=0
        do kk=liml,limu
          ia=cbal(kk)
          if (ia.eq.0) write(6,*)'problems with cube'
          if (ia.le.natom.and.ia.gt.0) then
            if(ast(ia).eq.0)then
              nnbr=nnbr+1
              nbra(nnbr)=ia
            endif
          else
c b+++++++++++++++++++++++++++++++++
            if (ia.ne.iaprec.and.eps(j).eq.0)then
c different from sclbp, I have to consider the object only if the
c midpoint is external O SE C'E' UN PORO E VEDERE IN SEGUITO
              iaprec=ia
c assuming any object is not buried
              nnbr=nnbr+1
              nbra(nnbr)=ia
            endif
c e++++++++++++++++++++++++++++++++
          endif
        end do
        do ii=1,nnbr
          ia=nbra(ii)
c b+++++++++++++++++++++++++++++++
          if (ia.gt.natom) then
            iii=ia-natom
            xq(1)=s1
            xq(2)=s2
            xq(3)=s3
c check if bgp is inside VdW of object
            call distobj(xq,dx,dy,dz,nobject,iii,0.0,dist,.false.,
     &  zeta,axdist)
c an object can compete with an atom for a midpoint only if this midpoint 
c is out of the object itself
            if (dist.ge.0..and.dist.lt.dmn) then
              dmn=dist
              iac=ia
              dr1=-dx*(radprb(1)-dist)
              dr2=-dy*(radprb(1)-dist)
              dr3=-dz*(radprb(1)-dist)
            end if
          else
c e++++++++++++++++++++++++++++++
            dx1=s1-xn1(1,ia)
            dx2=s2-xn1(2,ia)
            dx3=s3-xn1(3,ia)
            ds2=dx1*dx1+dx2*dx2+dx3*dx3
            dis=sqrt(ds2)-rad3(ia)
c dis= distance to atom surface
            if(dis.lt.dmn)then
              dmn=dis
              iac=ia
            endif
          endif
        end do

	if(iac.eq.0)then
         if (debug) write(6,*)i,j,'might be a cavity point',ix,iy,iz
	  ncav=ncav+1
c possibly a cavity point
	  goto 201
	else
c check to see if it is in the contact region of that atom by projecting it to
c the atom's acc surface and checking against the acc volumes of nearby atoms
          if (iac.le.natom) then
            dr1=s1-xn1(1,iac)
            dr2=s2-xn1(2,iac)
            dr3=s3-xn1(3,iac)
            dsr=sqrt(dr1*dr1+dr2*dr2+dr3*dr3)
            u1=xn1(1,iac)+dr1/dsr*r0(iac)
            u2=xn1(2,iac)+dr2/dsr*r0(iac)
            u3=xn1(3,iac)+dr3/dsr*r0(iac)
c b++++++++++++++++++++++++++++++
          else
            u1=s1-dr1
            u2=s2-dr2
            u3=s3-dr3
          endif
c e++++++++++++++++++++++++++++++

          it1=(u1-xo)*cbai
          it2=(u2-yo)*cbai
          it3=(u3-zo)*cbai
          liml=cbn1(it1+1+(lcb+1)*it2+(lcb+1)*(mcb+1)*it3)
          limu=cbn2(it1+1+(lcb+1)*it2+(lcb+1)*(mcb+1)*it3)
	  do kk=liml,limu
	    ia=cbal(kk)
            if (ia.le.natom) then
      	      dx1=u1-xn1(1,ia)
	      dx2=u2-xn1(2,ia)
	      dx3=u3-xn1(3,ia)
	      ds2=dx1*dx1+dx2*dx2+dx3*dx3
	      if(ds2.lt.rs2(ia))goto 201
            else
c b+++++++++++++++++++++++++++++++
              if (ia.ne.iac.and.eps(j).eq.0) then
                xq(1)=u1
                xq(2)=u2
                xq(3)=u3
                call distobj(xq,dx,dy,dz,nobject,ia-natom,radprb(1),
     &  dist,.true.,zeta,axdist)
                if (dist.lt.0.) go to 201 
c oriented distance from extended object surface
c if negative => reentrant region
              end if
c e+++++++++++++++++++++++++++++
            endif
	  end do
c it is in the contact region. flag the midpoint so it is not checked again
c iac is atom number...NOT increased by 1
	  eps(j)=-iac
          eps2(j)=-iac
	  goto 200
	endif

201	eps(j)=1
c eps = 1 means cavity or reentrant
c remap iepsmp
c b+++++++++++++++++++++++++++++++++++++
        if (iac.eq.0) then 
c this is an assumption, still to deeply understand meaning of cavity
c here and to improve this choice!WWW
           if (ia.gt.0) then
             imedia=iatmmed(ia)
           else
             write(6,*)'assigning arbitrary epsilon in cavity'
             imedia=iatmmed(1)
           endif
        else
           imedia=iatmmed(iac)
        endif
	  iepsmp(ix+imap(1,j),iy+imap(2,j),iz+imap(3,j),imap(4,j))=eps(j)
     &+imedia*epsdim
        eps2(j)=imedia
c     non specifico l'oggetto ma solo il mezzo, l'appartenenza verrà verificata in scale
c e+++++++++++++++++++++++
        
c check to see if the nearest neighbour status has been changed..
	ix2=ix
	iy2=iy
	iz2=iz
c if the nearest neighbour is a box boundary point then skip this
c since box boundary points can not also be dielctric boundary points
	if(j.eq.1) then
	  ix2=ix+1
	  if(ix2.eq.igrid) goto 200
	elseif(j.eq.2) then
	      iy2=iy+1
	      if(iy2.eq.igrid) goto 200
	    elseif(j.eq.3) then
	          iz2=iz+1
	          if(iz2.eq.igrid) goto 200
	        elseif(j.eq.4) then
	              ix2=ix-1
	              if(ix2.eq.1) goto 200
	            elseif(j.eq.5) then
	                  iy2=iy-1
	                  if(iy2.eq.1) goto 200
	                elseif(j.eq.6) then
	                      iz2=iz-1
	                      if(iz2.eq.1) goto 200
        end if
c
c b+++++++++++++
c once again one distinguishes between internal,external,
c internal bgp and external bgp
        iext=0
        ibgp=0

        itmp(1)=iabs(iepsmp(ix2,iy2,iz2,1))/epsdim
        itmp(2)=iabs(iepsmp(ix2,iy2,iz2,2))/epsdim
        itmp(3)=iabs(iepsmp(ix2,iy2,iz2,3))/epsdim
        itmp(4)=iabs(iepsmp(ix2-1,iy2,iz2,1))/epsdim
        itmp(5)=iabs(iepsmp(ix2,iy2-1,iz2,2))/epsdim
        itmp(6)=iabs(iepsmp(ix2,iy2,iz2-1,3))/epsdim
        if(itmp(1).eq.0) iext=1
        if(itmp(1).ne.itmp(6)) ibgp=1
        do cont=2,6
          if(itmp(cont).eq.0) iext=1
          if(itmp(cont).ne.itmp(cont-1)) ibgp=1
        end do
c debugging++++++++++++++++++++++++++++++
        if (debug) then
          nt=0
          if((iepsmp(ix2,iy2,iz2,1)/epsdim).gt.0)nt=nt+1
          if((iepsmp(ix2,iy2,iz2,2)/epsdim).gt.0)nt=nt+1
          if((iepsmp(ix2,iy2,iz2,3)/epsdim).gt.0)nt=nt+1
          if((iepsmp(ix2-1,iy2,iz2,1)/epsdim).gt.0)nt=nt+1
          if((iepsmp(ix2,iy2-1,iz2,2)/epsdim).gt.0)nt=nt+1
          if((iepsmp(ix2,iy2,iz2-1,3)/epsdim).gt.0)nt=nt+1
          if (nbe(nt).neqv.(ibgp.eq.1.and.iext.eq.1)) then
          write(6,*)'PROBLEMS3',ix2,iy2,iz2
          end if
        end if

c end+debugging++++++++++++++++++++++++++++++
c
	if((ibgp.eq.0).and.(bndeps(ix2,iy2,iz2,1).ne.0)) then
c reset bndeps for that point (i.e. remove bgp flag).
c a bgp become internal
          ibnumsurf=ibnumsurf-bndeps(ix2,iy2,iz2,2)
  	  bndeps(ix2,iy2,iz2,1)=0
          bndeps(ix2,iy2,iz2,2)=0
	  mr=mr+1
        else
          if(ibgp.eq.1.and.iext.eq.0.and.bndeps(ix2,iy2,iz2,2).eq.1)then
c an ext  bgp is turned into an internal bgp
            ibnumsurf=ibnumsurf-1
            bndeps(ix2,iy2,iz2,2)=0
          endif
        end if

	if(ibgp.eq.1.and.bndeps(ix2,iy2,iz2,1).eq.0) then
c create a new boundary point..
	  m=m+1
	  bndeps(ix2,iy2,iz2,1)=n2+m
	  ibnd(3*(n2+m)-2)=ix2
	  ibnd(3*(n2+m)-1)=iy2
	  ibnd(3*(n2+m))=iz2
          bndeps(ix2,iy2,iz2,2)=iext
          ibnumsurf=ibnumsurf+bndeps(ix2,iy2,iz2,2)
	end if
c e+++++++++++++
	end if	
c       now jump to the next midpoint of the same grid point
200	continue
c
c remap iepsmp in case there have been changes..
c (that is some  0's became -1's)
c ovvero: il midpoint deve restare esterno agli oggetti
c b+++++++++++++
            do jj=1,6
c             in this way I can deal with eps(jj)<0
              isign=1
c             iord=owner del midpoint jj prima della variazione o dopo eps=1
              iord=mod(iepsmp(ix+imap(1,jj),iy+imap(2,jj),iz+
     &             imap(3,jj),imap(4,jj)),epsdim)
c             l'ultima cambiata non ha sicuramente iord<0
c             ci possono essere iord<0 dovuti a primi vicini gia' cambiati
              if (iord.lt.0) goto 202
c             se e' cambiato in passo precedente non lo cambio piu'
              if(eps(jj).lt.0) then
                isign=-1
                if (iord.eq.0) iord=1
              end if
              jjj=iabs(iepsmp(ix+imap(1,jj),iy+imap(2,jj),iz+
     &              imap(3,jj),imap(4,jj)))/epsdim
              iepsmp(ix+imap(1,jj),iy+imap(2,jj),iz+imap(3,jj),
     &              imap(4,jj))=isign*(iord+jjj*epsdim)
c             lasciato iord col mod perche' se e'<> da 0 mantiene la sua identita'
202           continue
            end do

c at this point one still can trace what changes have been made
c check to see if this is still a boundary point
c once again one distinguishes between internal,external,
c internal bgp and external bgp
        iext=0
        ibgp=0
        itmp(1)=iabs(iepsmp(ix,iy,iz,1))/epsdim
        itmp(2)=iabs(iepsmp(ix,iy,iz,2))/epsdim
        itmp(3)=iabs(iepsmp(ix,iy,iz,3))/epsdim
        itmp(4)=iabs(iepsmp(ix-1,iy,iz,1))/epsdim
        itmp(5)=iabs(iepsmp(ix,iy-1,iz,2))/epsdim
        itmp(6)=iabs(iepsmp(ix,iy,iz-1,3))/epsdim
        if(itmp(1).eq.0) iext=1
        if(itmp(1).ne.itmp(6)) ibgp=1
        do cont=2,6
          if(itmp(cont).eq.0) iext=1
          if(itmp(cont).ne.itmp(cont-1)) ibgp=1
        end do
c debugging++++++++++++++++++++++++++++++
        if (debug) then	
          nt=0
          if((iabs(iepsmp(ix,iy,iz,1))/epsdim).gt.0)nt=nt+1
          if((iabs(iepsmp(ix,iy,iz,2))/epsdim).gt.0)nt=nt+1
          if((iabs(iepsmp(ix,iy,iz,3))/epsdim).gt.0)nt=nt+1
          if((iabs(iepsmp(ix-1,iy,iz,1))/epsdim).gt.0)nt=nt+1
          if((iabs(iepsmp(ix,iy-1,iz,2))/epsdim).gt.0)nt=nt+1
          if((iabs(iepsmp(ix,iy,iz-1,3))/epsdim).gt.0)nt=nt+1
          if (nbe(nt).neqv.(ibgp.eq.1.and.iext.eq.1)) then
            write(6,*)'PROBLEMS4',ix,iy,iz
            write(6,*)'epsdim=',epsdim,'ibgp=',ibgp,'iext=',iext
		  write(6,*)'itmp',itmp

            write(6,*)iepsmp(ix,iy,iz,1)
            write(6,*)iepsmp(ix,iy,iz,2)
            write(6,*)iepsmp(ix,iy,iz,3)
            write(6,*)iepsmp(ix-1,iy,iz,1)
            write(6,*)iepsmp(ix,iy-1,iz,2)
            write(6,*)iepsmp(ix,iy,iz-1,3)
          end if
        end if
c debugging++++++++++++++++++++++++++++++
c if not now a boundary element change bndeps
	if((iext.eq.0).or.(ibgp.eq.0)) then
         ibnumsurf=ibnumsurf-bndeps(ix,iy,iz,2)
         if(ibgp.eq.1) bndeps(ix,iy,iz,2)=iext
         if(ibgp.eq.0) then
	   bndeps(ix,iy,iz,1)=0
           bndeps(ix,iy,iz,2)=0
	   mr=mr+1
           if(iext.eq.1)write(6,*)'!!!born a new external point!!!'
         end if
	endif
c e++++++++++++
c  if end for whether bndeps is nonzero
	end if
c
c next boundary point  FINISH
	end do
c
	n1=n2+1
	n2=n2+m
	write(6,*)'bgp added m=',m,' bgp removed  mr =',mr
        if(m.gt.mpr)then
          ndv=ndv+1
          if(ndv.gt.2)then
            write(6,*)'surface iteration did not converge'
            stop
          endif
        else
            ndv=0
        endif
	if(m.gt.0) goto 100
	if(n2.gt.ibmx)then
	  write(6,*)'ibnd upper bound ',n2,' exceeds ibmx'
	  stop
	endif
c
	i_cbn1= memalloc(i_cbn1,0)
	i_cbn2= memalloc(i_cbn2,0)
	i_cbal= memalloc(i_cbal,0)

	call ddtime(tary)
	write(6,*)'time to grow re-entrant surface = ',tary(1)
	write(6,*)'no. cavity mid-points inaccessible to solvent = ',
     &	ncav

c consolidate the list, removing dead boundary points, adding new ones..
	j=0
	ncms=0
	i_ibgrd= memalloc(i_ibgrd,4*3*ibmx)
	do i=1,n2
	  ix=ibnd(3*i-2)
	  iy=ibnd(3*i-1)
	  iz=ibnd(3*i)

	  if(bndeps(ix,iy,iz,1).ne.0) then
	    j=j+1
	    bndeps(ix,iy,iz,1)=j
	    ibgrd(3*j-2)=ix
	    ibgrd(3*j-1)=iy
	    ibgrd(3*j)=iz
	  end if
c b+++++++++++++++++++++++++++++++++++++
        do jj=1,6
          nt=mod(iepsmp(ix+imap(1,jj),iy+imap(2,jj),iz+imap(3,jj),
     &  imap(4,jj)),epsdim)
          if (nt.lt.0) then
            iepsmp(ix+imap(1,jj),iy+imap(2,jj),iz+imap(3,jj),
     & imap(4,jj))=-iepsmp(ix+imap(1,jj),iy+imap(2,jj),iz+imap(3,jj),
     & imap(4,jj))
          if (nt.eq.-1) iepsmp(ix+imap(1,jj),iy+imap(2,jj),iz+
     & imap(3,jj),imap(4,jj))=iepsmp(ix+imap(1,jj),iy+imap(2,jj),iz+
     & imap(3,jj),imap(4,jj))-1
          end if
          if (debug) then
            nt=mod(iepsmp(ix+imap(1,jj),iy+imap(2,jj),iz+imap(3,jj),
     &  imap(4,jj)),epsdim)
            jjj=(iepsmp(ix+imap(1,jj),iy+imap(2,jj),iz+imap(3,jj),
     &  imap(4,jj))/epsdim)
            if (nt.eq.0.and.jjj.gt.0) then
              write(6,*)'PROBLEMS 5',ix,iy,iz,jj
            end if
          end if
        end do
c e++++++++++++++++++++++++++++++++++++
	end do

	if(j.gt.ibmx)stop 'no. ms points exceeds ibmx'
	ibnum=j
      write(6,*)'after surface elaboration ibnum= ',ibnum
      write(6,*)'    and               ibnumsurf= ',ibnumsurf
	i_ibgrd= memalloc(i_ibgrd,4*3*ibnum)
222     continue
        i_bndeps=memalloc(i_bndeps,0)
        i_ibnd= memalloc(i_ibnd,0)
c
c scale bondary grid point positions relative to acc data
        if(isolv.and.(irea.or.logs.or.lognl.or.isen.or.isch)) then
	  write(6,*)'scaling boundary grid points'
	  i_scspos= memalloc(i_scspos,4*3*ibnum)

	  do j=1,ibnum
	    scspos(3*j-2)=float(ibgrd(3*j-2))
  	    scspos(3*j-1)=float(ibgrd(3*j-1))
  	    scspos(3*j)=float(ibgrd(3*j))
	  end do
c b++++++++++
          i_scsnor=memalloc(i_scsnor,4*3*ibnum)
	  call sclbp(natom,igrid,xn1,scale,radprb,oldmid,ibnum,
     &	    extot,iall,scspos,scsnor,nobject,numbmol,ibnumsurf)
	  call ddtime(tary)
	  write(6,*)'time taken = ',tary(1)
	  write(6,*) iall,
     &	' points had to be assigned by global comparison'
          i_scsnor=memalloc(i_scsnor,0)
        endif

        if(isrf)then
          if (ionlymol) then
            i_egrid = 0
            i_egrid= memalloc(i_egrid,4*3*igrid*igrid*igrid)
            call msrf(natom,igrid,xn1,scale,radprb,oldmid,extot,ibnum,
     &  egrid,nobject,numbmol,ibnumsurf)
            i_egrid= memalloc(i_egrid,0)
          else
            write(6,*)'msrf routine cannot be run'
            write(6,*)'because there are also geometric objects'
          endif
        endif
c e++++++++++
        i_iab1= memalloc(i_iab1,0)
        i_iab2= memalloc(i_iab2,0)
        i_icume= memalloc(i_icume,0)

	i_r0= memalloc(i_r0,0)
	i_r02= memalloc(i_r02,0)
	i_rs2= memalloc(i_rs2,0)
	i_ast= memalloc(i_ast,0)

	goto 997
999	stop 'error opening ARCDAT file'
997	continue
	return
	end

        subroutine arcio(natm,nacc,arc,ast,iflg)
c       subroutine arcio(natm,nacc,arc,iflg)
	integer ast(natm)
	real arc(3,nacc)
	if(iflg.eq.0)then
	  read(1)ast
	  read(1)arc
	else
          write(1)ast
	  write(1)arc
	endif
	return
	end
       
c b++++++++++++++++++++++++++++++
        subroutine arcio1(nacc,arc)
        real arc(3,nacc)

        write(1)0
        write(1)arc
        return
        end
c e+++++++++++++++++++++++++++++++


