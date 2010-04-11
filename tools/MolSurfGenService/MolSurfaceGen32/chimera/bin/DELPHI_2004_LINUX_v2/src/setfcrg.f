	subroutine setfcrg(nqgrd,nqass,icount1a,icount1b,nmedia,
     &natom,idirectalg,nobject)
c
c	Mike Gilson's fancy charge distribution embedded into qdiffx.
c	A combination of Kim Sharp's chrgit1 and Anthony Nicholls' chrgup.
c       Grafting by Richard Friedman.
c	Latest version:6/2/89. First Version:4/25/89.
c
	include 'qdiffpar4.h'
	include 'qlog.h'
c
        integer iepsmp(igrid,igrid,igrid,3)
        logical*1 idebmap(igrid,igrid,igrid)
        real phimap(igrid,igrid,igrid)
c b+++++++++++++++++++++++
        integer nmedia,nqass,nqgrd,nobject
        real medeps(0:nmedia),atmeps(nqass),cgbp(5,1)
        real tmpmap(igrid,igrid,igrid),re,deb
        real gchrgtmp(1)
        integer idirectalg,nqgrdtonqass(nqgrd),ic1,epsdim 
c e++++++++++++++++++++++
	logical isum(3*ngrid),flag
	dimension gchrg(1),gchrgd(1),chrgv2(4,nqgrd)
	dimension qval(1),iqpos(1)
	dimension ddist2(500), rsave(500)
	dimension clist(4,50,500), nlist(500)
        dimension kb(3),dg(3)
	integer gchrgp(3,1),gchrg2(1)
	parameter (crit = .0001)
	data radmin,radmax,radstep / 1.2, 2.0, .005 /
c b+++++++++++++++++++++++
        i_cgbp=memalloc(i_cgbp,4*5*ibcmax)
c e++++++++++++++++++++++
c
c assign fractional charges to grid points, using phimap
c as a dummy array (set to zero again later)
c b+++++++++++++++++++++++
c       do i=1,igrid
c       do j=1,igrid
c       do k=1,igrid
c        phimap(k,j,i)=0.0 no longer needed, calloc superseded malloc
c        tmpmap(k,j,i)=0.0 no longer needed, calloc superseded malloc
c       end do
c       end do
c       end do
c e+++++++++++++++++++++++

        epsdim=natom+nobject+2
	difeps=epsin-epsout
	sixeps=epsout*6.0
	fpoh=fpi*scale
	debfct = epsout/(deblen*scale)**2
        do 9010 ig=1,nqgrd
          do 9001 i = 1,3
c
c truncate to nearest grid point
c
            kb(i) = chrgv2(i,ig)
c
c find position of charge in box in terms
c of fractional distance along edges
c
            dg(i) = chrgv2(i,ig) - kb(i)
9001	  continue
c
c loop over increasing radius to find suitable one
c
	  irmax = 0
	  do 9002 rmax = radmin, radmax, radstep
	    rmax2 = rmax*rmax
	    irmax = irmax + 1
	    rsave (irmax) = rmax
	    ilist = 0
	    ir = rmax + dg(1) + 1
c
c loop over all grid points within range of rmax:
c place base point of grid box containing the charge, at the origin, for now.
c
	    do 9003 i = -ir, ir
	      xdist = i - dg(1)
	      do 9004 j = -ir, ir
	        ydist = j - dg(2)
	        do 9005 k = -ir, ir
	          zdist = k - dg(3)
c
c calculate distance from current grid point to charge:
c
	          dist2 =  xdist*xdist + ydist*ydist + zdist*zdist
	          dist = sqrt(dist2)
c
c if grid point is closer than R, store the point and its distance:
c
		    if (dist2.le. Rmax2) then
	     		ilist = ilist + 1
	     		clist(1,ilist, irmax)  = i
	     		clist(2,ilist, irmax) = j
	     		clist(3,ilist, irmax) = k
	     		clist(4,ilist, irmax) = dist
	          endif
9005		continue
9004          continue
9003        continue
	    nlist(irmax) = ilist
c
c generate weighting factors for this rmax:
c sum normalizes the weighting to one:
c
	    sum = 0
	    do 9006 il = 1, nlist(irmax)
	      clist(4,il, irmax) = Rmax - clist(4,il, irmax)
	      sum = sum + clist(4,il, irmax)
9006	    continue
c
c normalize the weighting factors to sum to one:
c
	    do 9007 il = 1, nlist(irmax)
	      clist(4,il, irmax) = clist(4,il, irmax)/sum
9007	    continue
c
c calculate center of charge for this rmax:
c
	    xsum = 0
	    ysum = 0
	    zsum = 0
	    do 9008 il = 1, nlist(irmax)
	      xsum = xsum + clist(4,il, irmax) * clist(1,il, irmax)
	      ysum = ysum + clist(4,il, irmax) * clist(2,il, irmax)
	      zsum = zsum + clist(4,il, irmax) * clist(3,il, irmax)
9008	    continue
c	  print *, 'center of charge in map:' , xsum,ysum, zsum
c	  print *, 'actual location:        ', dg(1), dg(2), dg(3)
c
c check whether criterion is satisfied, and if so, exit rmax loop.
c
	    ddx = dg(1) - xsum
	    ddy = dg(2) - ysum
	    ddz = dg(3) - zsum
	    ddist2(irmax) = ddx * ddx + ddy*ddy + ddz * ddz
	    if (ddist2(irmax) .le.crit) goto 1000
c
c otherwise, try another cutoff radius:		
9002      continue
c
c if loop gets finished without a radius yielding good enough
c results, print warning,and use the best cutoff radius found:
c	print *, 'Criterion not satisfied for charge #, ', iq
c	print *, ' Using best cutoff radius found...'
c
c	  call minimum (ddist2, irmax, ichoice, dmin)
c

	  dmin = 100000
	  do 9000 i = 1, irmax
	    if (ddist2(i).lt.dmin) then
	      dmin = ddist2(i)
	      ichoice = i
	    endif
9000	  continue

c---------------------------------------------------
	  dmin = sqrt (dmin)
	  rmax = rsave(ichoice)
	  goto 1500

1000	  continue
	  ichoice = irmax
	  dmin = sqrt(ddist2(ichoice))

1500	  continue

c
c now we know what set of grids we're distributing the charge over
c (clist(1-3, 1-ilist(ichoice), ichoice) for ichoice), and the weighting
c (clist(4,1-ilist, ichoice)...
c now, distribute the charge:
c
	  do 9009 ilist = 1, nlist(ichoice)
c
c get grid point by adding offset to it
c
	    kx = kb(1) + clist(1,ilist,ichoice)
	    ky = kb(2) + clist(2,ilist,ichoice)
	    kz = kb(3) + clist(3,ilist,ichoice)
c
c make sure grid point is within the big box (should be a problem only
c in cases where box edge cuts through
c or very near the protein):
c
	    flag = .false.
   	    if (kx.lt.1 ) then
	      kx = 1
	      flag = .true.
	    endif
   	    if (ky .lt.1) then
	      ky = 1
	      flag = .true.
	    endif
   	    if (kz .lt.1) then
	      kz = 1
	      flag = .true.
	    endif
   	    if (kx.gt.igrid) then
	      kx = igrid
	      flag = .true.
	    endif
   	    if (ky.gt.igrid)then
	      ky = igrid
	      flag = .true.
	    endif
   	    if (kz.gt.igrid) then
	      kz = igrid
	      flag = .true.
	    endif

	    if(flag)then
	      write(6,*)' problem for charge at', (chrgv2(j,ig),j=1,3)
	    end if

            re=clist(4,ilist,ichoice)*chrgv2(4,ig)
	    phimap(kx,ky,kz)= phimap(kx,ky,kz) + re

9009	  continue

9010    continue
c set up odd/even logical array
	do 10 i=1,3*igrid,2
10	  isum(i)=.true.
	do 20 i=2,(3*igrid-1),2
20	  isum(i)=.false.
c
c find which grid points have charge assigned to them
c (will use this array later to calculate grid energy)
c
	n=0
        do k=2,igrid-1
          do j=2,igrid-1
            do i=2,igrid-1
                if(phimap(i,j,k).ne.0)n=n+1
	    enddo
	  enddo
	enddo
        i_gchrgp=memalloc(i_gchrgp,4*3*n)
        i_gchrg=memalloc(i_gchrg,4*n)
        i_gchrgd=memalloc(i_gchrgd,4*n)
        i_gchrg2=memalloc(i_gchrg2,4*n)
	i_qval=memalloc(i_qval,4*n)
        i_iqpos=memalloc(i_iqpos,4*n)

        n=0
	do 100 k=2,igrid-1
	  do 110 j=2,igrid-1
	    do 120 i=2,igrid-1
		if(phimap(i,j,k).ne.0) then
		n=n+1
		gchrgp(1,n)=i
		gchrgp(2,n)=j
		gchrgp(3,n)=k
		gchrg(n)=phimap(i,j,k)
		phimap(i,j,k)=0.0
		end if
120	 continue
110	 continue
100	 continue
	icount1b=n
        if (icount1b.gt.ngcrg) then
          write(6,*)'Fatal error: icount1b ',icount1b,'exceeds ngcrg'
     &,ngcrg
          write(6,*)'Please Increase ngcrg'
          stop
        end if


c b++++++++++++++++++++June 2001++to save memory waste time++++++
        do 9110 ig=1,nqgrd
          ic1=nqgrdtonqass(ig)
          do 9101 i = 1,3
c
c truncate to nearest grid point
c
            kb(i) = chrgv2(i,ig)
c
c find position of charge in box in terms
c of fractional distance along edges
c
            dg(i) = chrgv2(i,ig) - kb(i)
9101      continue
c
c loop over increasing radius to find suitable one
c
          irmax = 0
          do 9102 rmax = radmin, radmax, radstep
            rmax2 = rmax*rmax
            irmax = irmax + 1
            rsave (irmax) = rmax
            ilist = 0
            ir = rmax + dg(1) + 1
c
c loop over all grid points within range of rmax:
c place base point of grid box containing the charge, at the origin, for now.
c
            do 9103 i = -ir, ir
              xdist = i - dg(1)
              do 9104 j = -ir, ir
                ydist = j - dg(2)
                do 9105 k = -ir, ir
                  zdist = k - dg(3)
c
c calculate distance from current grid point to charge:
c
                  dist2 =  xdist*xdist + ydist*ydist + zdist*zdist
                  dist = sqrt(dist2)
c
c if grid point is closer than R, store the point and its distance:
c
                    if (dist2.le. Rmax2) then
                        ilist = ilist + 1
                        clist(1,ilist, irmax)  = i
                        clist(2,ilist, irmax) = j
                        clist(3,ilist, irmax) = k
                        clist(4,ilist, irmax) = dist
                  endif
9105            continue
9104          continue
9103        continue
            nlist(irmax) = ilist
c
c generate weighting factors for this rmax:
c sum normalizes the weighting to one:
c
            sum = 0
            do 9106 il = 1, nlist(irmax)
              clist(4,il, irmax) = Rmax - clist(4,il, irmax)
              sum = sum + clist(4,il, irmax)
9106        continue
c
c normalize the weighting factors to sum to one:
c
            do 9107 il = 1, nlist(irmax)
              clist(4,il, irmax) = clist(4,il, irmax)/sum
9107        continue
c
c calculate center of charge for this rmax:
c
            xsum = 0
            ysum = 0
            zsum = 0
            do 9108 il = 1, nlist(irmax)
              xsum = xsum + clist(4,il, irmax) * clist(1,il, irmax)
              ysum = ysum + clist(4,il, irmax) * clist(2,il, irmax)
              zsum = zsum + clist(4,il, irmax) * clist(3,il, irmax)
9108        continue
c         print *, 'center of charge in map:' , xsum,ysum, zsum
c         print *, 'actual location:        ', dg(1), dg(2), dg(3)
c
c check whether criterion is satisfied, and if so, exit rmax loop.
c
            ddx = dg(1) - xsum
            ddy = dg(2) - ysum
            ddz = dg(3) - zsum
            ddist2(irmax) = ddx * ddx + ddy*ddy + ddz * ddz
            if (ddist2(irmax) .le.crit) goto 1100
c
c otherwise, try another cutoff radius:
9102      continue
c
c if loop gets finished without a radius yielding good enough
c results, print warning,and use the best cutoff radius found:
c       print *, 'Criterion not satisfied for charge #, ', iq
c       print *, ' Using best cutoff radius found...'
c
c         call minimum (ddist2, irmax, ichoice, dmin)
c

          dmin = 100000
          do 9100 i = 1, irmax
            if (ddist2(i).lt.dmin) then
              dmin = ddist2(i)
              ichoice = i
            endif
9100      continue

c---------------------------------------------------
          dmin = sqrt (dmin)
          rmax = rsave(ichoice)
          goto 1510

1100      continue
          ichoice = irmax
          dmin = sqrt(ddist2(ichoice))

1510      continue

c
c now we know what set of grids we're distributing the charge over
c (clist(1-3, 1-ilist(ichoice), ichoice) for ichoice), and the weighting
c (clist(4,1-ilist, ichoice)...
c now, distribute the charge:
c
          do 9109 ilist = 1, nlist(ichoice)
c
c get grid point by adding offset to it
c
            kx = kb(1) + clist(1,ilist,ichoice)
            ky = kb(2) + clist(2,ilist,ichoice)
            kz = kb(3) + clist(3,ilist,ichoice)
c
c make sure grid point is within the big box (should be a problem only
c in cases where box edge cuts through
c or very near the protein):
c
            flag = .false.
            if (kx.lt.1 ) then
              kx = 1
              flag = .true.
            endif
            if (ky .lt.1) then
              ky = 1
              flag = .true.
            endif
            if (kz .lt.1) then
              kz = 1
              flag = .true.
            endif
            if (kx.gt.igrid) then
              kx = igrid
              flag = .true.
            endif
            if (ky.gt.igrid)then
              ky = igrid
              flag = .true.
            endif
            if (kz.gt.igrid) then
              kz = igrid
              flag = .true.
            endif

            if(flag)then
              write(6,*)' problem for charge at', (chrgv2(j,ig),j=1,3)
            end if

            re=clist(4,ilist,ichoice)*chrgv2(4,ig)
            deb=0.
            if (idebmap(kx,ky,kz)) deb=1.
            phimap(kx,ky,kz)=phimap(kx,ky,kz)+re/(6.*atmeps(ic1)+
     &  debfct*deb)
9109      continue

9110    continue
c e++++++++++++++++++++++++++++++++++++++++++++

        i_gchrgtmp=memalloc(i_gchrgtmp,4*icount1b)
c
c determine how many charged grid points are odd
c
	icount1a=0
	do 200 i=1,n
	itemp=gchrgp(1,i)+gchrgp(2,i)+gchrgp(3,i)
	if(isum(itemp)) icount1a=icount1a+1
200	continue
c
c set up odd/even pointer array, to be used in making qval
c and iqpos
c
	i1=0
	i2=icount1a
	do 300 i=1,n
	  itemp=gchrgp(1,i)+gchrgp(2,i)+gchrgp(3,i)
	  if(isum(itemp)) then
	    i1=i1+1
	    gchrg2(i)=i1
	  else
	    i2=i2+1
	    gchrg2(i)=i2
	  end if
300	continue
c
c determine denominator at all charged grid points
c
	ib=0
	epsins6= 6.0*epsin 
	do 400 i=1,n
	iz=gchrgp(3,i)
	iy=gchrgp(2,i)
	ix=gchrgp(1,i)
        itemp=0
c cambiato da mod a div, mi dovrebbe servire solo il mezzo
        if((iepsmp(ix,iy,iz,1)/epsdim).ne.0) itemp=itemp+1
        if((iepsmp(ix,iy,iz,2)/epsdim).ne.0) itemp=itemp+1
        if((iepsmp(ix,iy,iz,3)/epsdim).ne.0) itemp=itemp+1
        if((iepsmp(ix-1,iy,iz,1)/epsdim).ne.0) itemp=itemp+1
        if((iepsmp(ix,iy-1,iz,2)/epsdim).ne.0) itemp=itemp+1
        if((iepsmp(ix,iy,iz-1,3)/epsdim).ne.0) itemp=itemp+1
c itemp=number of internal closest midpoints
c b++++++++++++++++++++
        deb=0.
        if (idebmap(ix,iy,iz)) deb=1.
        if (idirectalg.eq.0)  then
           gchrgd(i)=itemp*difeps + debfct*deb + sixeps
        else
           temp=0.0
           itmp=iepsmp(ix,iy,iz,1)/epsdim
           temp=temp+medeps(itmp)
           itmp=iepsmp(ix,iy,iz,2)/epsdim
           temp=temp+medeps(itmp)
           itmp=iepsmp(ix,iy,iz,3)/epsdim
           temp=temp+medeps(itmp)
           itmp=iepsmp(ix-1,iy,iz,1)/epsdim
           temp=temp+medeps(itmp)
           itmp=iepsmp(ix,iy-1,iz,2)/epsdim
           temp=temp+medeps(itmp)
           itmp=iepsmp(ix,iy,iz-1,3)/epsdim
           temp=temp+medeps(itmp)
c here temp=sum(eps of 6 closest midpoints)
           gchrgd(i)=temp+ debfct*deb
        end if
c e++++++++++++++++++++
	if(itemp.ne.6) then
	ib=ib+1
	cgbp(1,ib)=ix
	cgbp(2,ib)=iy
	cgbp(3,ib)=iz
c b++++++++++++++++++++
	cgbp(4,ib)=gchrgtmp(i)*fpoh
c       cgbp(6,ib)=tmpmap1(ix,iy,iz)
c e++++++++++++++++++++
	cgbp(5,ib)=gchrg2(i)
	end if
400	continue
        i_gchrgtmp=memalloc(i_gchrgtmp,0)
	ibc=ib
        i_cgbp=memalloc(i_cgbp,4*5*ibc)
	write(6,*) '# grid points charged and at boundary=',ib
c
c make qval, fpoh term so potentials will be in kt/e
c
	do 500 i=1,n
	j=gchrg2(i)
	qval(j)=gchrg(i)*fpoh/gchrgd(i)
500	continue
        i_gchrgd=memalloc(i_gchrgd,0)
c
c make iqpos
c
	isgrid=igrid**2
	do 600 i=1,n
	j=gchrg2(i)
	ix=gchrgp(1,i)
	iy=gchrgp(2,i)
	iz=gchrgp(3,i)
	iw=1+ix+igrid*(iy-1)+isgrid*(iz-1)
	iv=iw/2
	iqpos(j)=iv
600	continue
        i_gchrg2=memalloc(i_gchrg2,0)
c
c end of chrgup, return with qval,iqpos and gchrgp and gchrg
c also icount1a, icount1b
c b+++++++++++++++++++++++++++++++
        i_tmpmap=memalloc(i_tmpmap,0)
c       i_tmpmap1=memalloc(i_tmpmap1,0)
c e+++++++++++++++++++++++++++++++
	return
	end
