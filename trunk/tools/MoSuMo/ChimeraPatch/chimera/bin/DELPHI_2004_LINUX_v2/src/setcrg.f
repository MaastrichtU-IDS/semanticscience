	subroutine setcrg(nqgrd,nqass,icount1a,icount1b,nmedia,
     &natom,idirectalg,nobject)
c
c gchrg is the fractional charge in electron units assigned to
c each grid point, gchrgp is the position of each such charge on the
c grid.
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
        real re,deb
c       real tmpmap(igrid,igrid,igrid),re,deb
c tmpmap1(igrid,igrid,igrid),radius,cost,rad3(natom)
        real gchrgtmp(1)
        integer idirectalg,nqgrdtonqass(nqgrd),ic1,epsdim
c ,ii,crgatn(1)
c e++++++++++++++++++++++
	logical isum(3*ngrid)
	dimension gchrg(1),gchrgd(1),chrgv2(4,nqgrd)
	dimension qval(1),iqpos(1)
    	integer gchrgp(3,1),gchrg2(1)
c b+++++++++++++++++++++++
c       i_tmpmap=memalloc(i_tmpmap,4*igrid*igrid*igrid)
c       i_gchrgtmp=memalloc(i_gchrgtmp,4*ngcrg)
        i_cgbp=memalloc(i_cgbp,4*5*ibcmax)
c e++++++++++++++++++++++
c
c assign fractional charges to grid points, using phimap
c as a dummy array (set to zero again later)
c       do i=1,igrid
c       do j=1,igrid
c       do k=1,igrid
c        phimap(k,j,i)=0.0 no longer needed, calloc superseded malloc
c        tmpmap(k,j,i)=0.0 no longer needed, calloc superseded malloc
c        tmpmap1(k,j,i)=0.0
c       end do
c       end do
c       end do
c 
	difeps=epsin-epsout
        epsdim=natom+nobject+2
	sixeps=epsout*6.0
	fpoh=fpi*scale
	debfct = epsout/(deblen*scale)**2
c
	do 821 ig=1,nqgrd 
	  kb1=chrgv2(1,ig)
	  kb2=chrgv2(2,ig)
	  kb3=chrgv2(3,ig)
	  do 822 ix=0,1
	    i=kb1+ix
	    cg1=kb1-chrgv2(1,ig)+1-ix
	    do 823 iy=0,1
	      j=kb2+iy
	      cg2=kb2-chrgv2(2,ig)+1-iy
              do 824 iz=0,1
                k=kb3+iz
		cg3=kb3-chrgv2(3,ig)+1-iz
                re=abs(cg1*cg2*cg3)*chrgv2(4,ig)
	        phimap(i,j,k)=phimap(i,j,k)+re
824	      continue
823	    continue
822	  continue
821	continue

        n=0
        do k=2,igrid-1
          do j=2,igrid-1
            do i=2,igrid-1
              if(phimap(i,j,k).ne.0.) n=n+1
            enddo
          enddo
        enddo

        i_gchrgp=memalloc(i_gchrgp,4*3*n)
        i_gchrg=memalloc(i_gchrg,4*n)
        i_gchrgd=memalloc(i_gchrgd,4*n)
        i_gchrg2=memalloc(i_gchrg2,4*n)
        i_qval=memalloc(i_qval,4*n)
        i_iqpos=memalloc(i_iqpos,4*n)
        i_gval=memalloc(i_gval,4*n)
c
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
	do 100 k=2,igrid-1
	  do 110 j=2,igrid-1
	    do 120 i=2,igrid-1
	      if(phimap(i,j,k).ne.0.) then
		n=n+1
		gchrgp(1,n)=i
		gchrgp(2,n)=j
		gchrgp(3,n)=k
		gchrg(n)=phimap(i,j,k)
		phimap(i,j,k)=0.0
	      end if
120	    continue
110	  continue
100	continue 
	icount1b=n
        if (icount1b.gt.ngcrg) then
          write(6,*)'WARNING!! icount1b',icount1b,'exceeds ngcrg',ngcrg
          write(6,*)'It is advisable to increase it'
        end if
    
c
c b++++++++++++++++++++June 2001++to save memory waste time++++++
        do 1821 ig=1,nqgrd
          kb1=chrgv2(1,ig)
          kb2=chrgv2(2,ig)
          kb3=chrgv2(3,ig)
          ic1=nqgrdtonqass(ig)
          do 1822 ix=0,1
            i=kb1+ix
            cg1=kb1-chrgv2(1,ig)+1-ix
            do 1823 iy=0,1
              j=kb2+iy
              cg2=kb2-chrgv2(2,ig)+1-iy
              do 1824 iz=0,1
                k=kb3+iz
                cg3=kb3-chrgv2(3,ig)+1-iz
                re=abs(cg1*cg2*cg3)*chrgv2(4,ig)
                deb=0.
                if (idebmap(i,j,k)) deb=1.
                phimap(i,j,k)=phimap(i,j,k)+re/(6.*atmeps(ic1)+
     &                          debfct*deb)
1824          continue
1823        continue
1822      continue
1821    continue

        i_gchrgtmp=memalloc(i_gchrgtmp,4*icount1b)
        do 1101 n=1,icount1b
          i=gchrgp(1,n)
          j=gchrgp(2,n)
          k=gchrgp(3,n)
          gchrgtmp(n)=phimap(i,j,k)
1101    continue
          
        do 1100 k=2,igrid-1
          do 1110 j=2,igrid-1
            do 1120 i=2,igrid-1
              phimap(i,j,k)=0.0
1120        continue
1110      continue
1100    continue


c e+++++++++++++++++++++++++++++++++++++++++++++
        if(iwgcrg) then
        call wrtgcrg(gcrgnam,gcrglen,icount1b,gchrgp,gchrg,nmedia,scale,
     &  medeps,epkt)
        end if
c determine how many charged grid points are odd
c 
	icount1a=0
	do 200 i=1,icount1b
	itemp=gchrgp(1,i)+gchrgp(2,i)+gchrgp(3,i)
	if(isum(itemp)) icount1a=icount1a+1
200	continue 
c
c set up odd/even pointer array, to be used in making qval
c and iqpos
c 
	i1=0
	i2=icount1a
	do 300 i=1,icount1b
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
	ico=0
	do 400 i=1,icount1b
	  iz=gchrgp(3,i)
	  iy=gchrgp(2,i)
	  ix=gchrgp(1,i)
	  ieps=0
c cambiato da mod a div, mi dovrebbe servire solo il mezzo
	  if((iepsmp(ix,iy,iz,1)/epsdim).ne.0) ieps=ieps+1
	  if((iepsmp(ix,iy,iz,2)/epsdim).ne.0) ieps=ieps+1
	  if((iepsmp(ix,iy,iz,3)/epsdim).ne.0) ieps=ieps+1
	  if((iepsmp(ix-1,iy,iz,1)/epsdim).ne.0) ieps=ieps+1
	  if((iepsmp(ix,iy-1,iz,2)/epsdim).ne.0) ieps=ieps+1
	  if((iepsmp(ix,iy,iz-1,3)/epsdim).ne.0) ieps=ieps+1
c itemp=number of internal closest midpoints
	  itemp=ieps
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
	    if(itemp.eq.0) ico=ico+1
	    cgbp(1,ib)=ix 
	    cgbp(2,ib)=iy
	    cgbp(3,ib)=iz 
c b++++++++++++++++++++
	    cgbp(4,ib)=gchrgtmp(i)*fpoh
c e++++++++++++++++++++
	    cgbp(5,ib)=gchrg2(i)
	  end if 
400	continue 
        i_gchrgtmp=memalloc(i_gchrgtmp,0)
        ibc=ib
        i_cgbp=memalloc(i_cgbp,4*5*ibc)
	write(6,*) 'no. grid points charged and not internal=',ibc
	if(ico.ne.0) write(6,*) "## out of them,",ico," charged points 
     &are in solution ##"
c
c make qval, fpoh term so potentials will be in kt/e
c 
	do 500 i=1,icount1b
	  j=gchrg2(i)
	  qval(j)=gchrg(i)*fpoh/gchrgd(i)
	  gval(j)=gchrg(i)
500	continue 
        i_gchrgd=memalloc(i_gchrgd,0) 
c
c make iqpos
c 
	isgrid=igrid**2
	do 600 i=1,icount1b
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
	close (2)
	return
	end 
