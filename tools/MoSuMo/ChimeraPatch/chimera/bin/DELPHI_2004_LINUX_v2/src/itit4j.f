        subroutine itit(idpos,db,sf1,sf2,iqpos,qval,icount2a,icount2b,
     &  icount1a,icount1b,spec,nsp,phimap,phimap1,phimap2,phimap3,
     &  bndx,bndy,bndz,bndx1,bndx2,bndx3,bndx4,gval,idirectalg,cgbp)

c
c
c NOTE THIS HAS BEEN ALTERED TO GIVE THE CONVERGENCE TO THE EXACT
C SOLUTION, WHICH IS INPUTTED VIA OPTION 3,(AND NOW WITH GAUSS
C SIEDEL IMPLEMENTED, WITH MAPPED SUBARRAYS.)
c
c  finally what we`ve all been waiting for-
c do the actual pb equation iteration
c first the linear, with relaxation parameter 1.
c then non-linear with relaxation parameter 0.6
c
c this is a modified iteration routine which runs at about
c three times that of the original version. this has been 
c accomplished by several features which will be mentioned
c at the appropiate juncture.
c note that the arrays slab,old and denom no longer exist
c and that epsmap is only used in setting up arrays
c in their place are several arrays, the two biggest being
c phimap2 and sf.
c however, the array space accessed in the main inner loop
c is no larger than before, i.e. memory requirements should
c not be much different.
c
c some notes on array sizes. there can be no more than 10000
c charges, or 12000 boundary elements, or 40000 high potential salt
c sites (for the nonlinear). also, for the latter the potential
c in salt should not exceed 10kt
c
	include 'qdiffpar5.h'
	include 'qlog.h'

        real cgbp(5,ibc)
	parameter ( nxran = 60 )
	parameter ( nyran = 20 )
	dimension rmsl(nxran),rmsn(nxran),rmaxl(nxran),rmaxn(nxran)
	dimension qval(icount1b)
	dimension db(6,nsp),sf1(nhgp),sf2(nhgp)
	integer iqpos(icount1b),idpos(nsp)
        integer idirectalg
	dimension bndx1(nbgp),bndx2(nbgp),bndx3(nbgp),bndx4(nbgp)
	dimension bndx(nbgp),bndy(nbgp),bndz(nbgp),grdn(5)
	character*24 day
	character*1 symb
	character*70 title,iplot(nyran)
	logical qstopper,resdat,once,igt
	integer star,fin,sta1(ngrid),sta2(ngrid),fi1(ngrid),fi2(ngrid)
        real phimap1(nhgp),phimap2(nhgp),phimap3(ngp)
        real phimap(igrid,igrid,igrid)
c-------------------------------------------------------
        character*24 fdate
        external fdate
        start = cputime(0.0)
        day=fdate()
        write(6,*)'now iterating at: ',day(12:19)
c-------------------------------------------------------
c allocate memory to arrays

c some initialization
c
c       open(52,file='data',form='formatted')
c        do i=1,38
c        write(52,*)db(1,i),db(2,i),db(3,i),db(4,i),db(5,i),db(6,i)
c        end do
c       close(52) 

	once=.true.
	icount2abac=icount2a
	icount2bbac=icount2b 
	epsrat=epsout/epsin 
	sixth = 1./6.
c	th120 = 1./120.
	icgrid=igrid**3
	ihgd=(igrid+1)/2
	if(icon2.eq.0) then
	icon1=10
	icon2=1
	end if 
	if(icon1.gt.nlit) icon1=nlit 
c
C
	do 9000 i = 1,nxran
	  rmsl(i) = 0.0
	  rmsn(i) = 0.0
	  rmaxl(i) = 0.0
	  rmaxn(i) = 0.0
9000	continue
      npoint = (igrid-2)**3
c
c
c comment out for cray version 14, nov 88, kas
c
c ---------------------------------------------
c MAIN SET UP ROUTINE	
c ---------------------------------------------
c
cif(iper(1)) then
cn=0
cdo 440 iz=2,igrid-1
c  iadd1=(iz-1)*igrid*igrid 
c  do 441 iy=2,igrid-1
c    iadd2=(iadd1+(iy-1)*igrid +2)/2
c    n=n+1
c    bndx(n)=iadd2
c441	  continue
c440     continue
cidif1x=(igrid-2)/2
cidif2x=idif1x+1
cinc1xa=1
cinc1xb=0
cinc2xa=0
cinc2xb=1
cend if 
	if(iper(2)) then
	n=0
	do 442 iz=2,igrid-1
	  iadd1=(iz-1)*igrid*igrid 
	  do 443 ix=2,igrid-1
	    iadd2=(iadd1+ix+1)/2
	    n=n+1
    	    bndy(n)=iadd2
443       continue
442     continue
	idif1y=igrid*(igrid-2)/2
	idif2y=idif1y+1
	inc1ya=(igrid/2)+1
	inc1yb=inc1ya-1
	inc2ya=inc1yb
	inc2yb=inc1ya
	end if
	if(iper(3).or.iper(6)) then
	n=0
	do 444 ix=2,igrid-1
	  iadd1=ix+1
	  do  445 iy=2,igrid-1
	    iadd2=(iadd1+(iy-1)*igrid)/2
	    n=n+1
	    bndz(n)=iadd2
445	  continue
444	continue
	idif1z=igrid*igrid*(igrid-2)/2
	idif2z=idif1z+1
	inc1za=((igrid**2)/2)+1
	inc1zb=inc1za
	inc2za=inc1zb
	inc2zb=inc1za
	end if
c
c
c END OF SET UP	
c
c remove qstopper file if it already exists
c
      inquire(file='qstop.test',exist=qstopper)
      if(qstopper) then
        open(30,file='qstop.test')
        close(30,status='delete')
        qstopper=.false.
      end if
c
c check for resolution data
c commented out, by kas, 29my 89, as syntax not vax compatible, and obseleted
c
c
c     inquire(file='res.dat',exist=resdat)
c     if(resdat) then
c       open(31,file='res.dat')
c       read(31,*,err=65) res1,res2
c       if(nnit.ne.0) then
c         read(31,*,err=55) res3,res4
c55       continue
c       else
c         res3=0.0
c         res4=0.0
c       endif
c       close(31)
c65   else
        resdat = .false.
c b++commented out by Walter (06-2001), convergence criteria given by user
c       res1=0.0
c       res2=0.0
c e++++++++++++++++++++++++++++++++++++++++++++++++++++
        res3=0.0
        res4=0.0
c     end if
      if(resdat) then 
        write(6,*) ' '
        write(6,*) 'linear resolution criteria are:',res1,res2,res5
        if(nnit.ne.0) then
          write(6,*) 'non-linear resolution criteria are:',res3,res4
        end if
        write(6,*) ' '
      end if 
c
      write(6,*) ' '
      write(6,*) ' '
      if(gten.gt.0.0)then
	write(6,*) 
     &	'  rms-change     max change    grid energy    #iterations'
      else
     	write(6,*) '  rms-change     max change       #iterations'
      endif
c
c set up start and stop vectors
	sta1(2)=(igrid**2 + igrid +4)/2
	sta2(2)=sta1(2)-1
	fi1(2)=igrid**2 - (igrid+1)/2
	fi2(2)=fi1(2)
	itemp1=igrid + 2
	itemp2=igrid**2 -igrid -2
	do 225 i=3,igrid-1
	sta1(i)=fi1(i-1) + itemp1
	sta2(i)=fi2(i-1) + itemp1
	fi1(i)=sta1(i-1) + itemp2
	fi2(i)=sta2(i-1) + itemp2
225     continue
c
c also
c
	lat1= (igrid-1)/2
	lat2= (igrid+1)/2
	long1= (igrid**2 - 1)/2
	long2= (igrid**2 + 1)/2
c 
      ires=0
c
	if(icheb) then
	om2=1.0
	goto 333
	end if
c
	om2=2.0/(1.0 + sqrt(1 - spec))
	do 801 ix=1,(icgrid+1)/2
	  sf1(ix)=sf1(ix)*om2
	  sf2(ix)=sf2(ix)*om2
801	continue
	do 802 ix=1,icount1b 
	  qval(ix)=qval(ix)*om2
802	continue 
	do 803 iy=1,6
	  do 804 ix=1,icount2b
	  db(iy,ix)=db(iy,ix)*om2
804	continue
803	continue 
	sixth=sixth*om2 
c
333	om1=1.0-om2
c
	i=1
c
        iw=1
	do 311 iz=1,igrid
	  do 312 iy=1,igrid
	    do 313 ix=1,igrid
	    phimap3(iw)=phimap(ix,iy,iz)
	    iw=iw+1
313         continue
312       continue
311     continue
c
c 
1689    do 314 ix=1,(icgrid+1)/2
	  iy=ix*2
          phimap1(ix)=phimap3(iy-1)
          phimap2(ix)=phimap3(iy)
314	continue
c
        ihgd2=ihgd-1
c b+++++++++++++++++++++++++++++++++++++++
        if (.not.iper(1)) then
c e+++++++++++++++++++++++++++++++++++++++
c       set x boundary values 
c 
	  star=(igrid+1)/2
  	  iy=(igrid*(igrid+1)/2) - igrid + 1
	  fin=(igrid*(igrid-1)-2)/2
	  do 9211 ix=star,fin
	    iy=iy+igrid
	    bndx1(ix)=phimap1(iy)
	    bndx2(ix)=phimap1(iy+ihgd2)
9211      continue
c 
	  star=(igrid+2)/2
	  iy=(igrid*(igrid+2)/2) - igrid +1
	  fin=(igrid*(igrid-1)-1)/2
	  do 8211 ix=star,fin
     	    iy=iy+igrid
	    bndx3(ix)=phimap2(iy)
	    bndx4(ix)=phimap2(iy+ihgd2)
8211      continue
        end if
c

1000    continue
c
c clear rms, max change
c
	rmsch = 0.0
	rmxch = 0.00

c
c if there is no salt then the main loop is executed without sf
c saving about 15% in execution time
c
	if(rionst.gt.0.0) then
          do 9004 n = 2, igrid-1
	    star=sta1(n)
	    fin=fi1(n)
            do 9006 ix = star,fin
              temp1 = phimap2(ix) + phimap2(ix-1)
              temp2 = phimap2(ix+lat1) + phimap2(ix-lat2)
              temp3 = phimap2(ix+long1) + phimap2(ix-long2)
       	      phimap1(ix)=phimap1(ix)*om1+(temp1+temp2+temp3)*sf1(ix)
9006	    continue
9004	  continue
c otherwise the main loop is as below:
        else
          do 9104 n = 2, igrid-1
	    star=sta1(n)
	    fin=fi1(n)
            do 9106 ix = star,fin
              temp1 = phimap2(ix) + phimap2(ix-1)
              temp2 = phimap2(ix+lat1) + phimap2(ix-lat2)
              temp3 = phimap2(ix+long1) + phimap2(ix-long2)
      	      phimap1(ix) = phimap1(ix)*om1 + (temp1+temp2+temp3)*sixth
9106	    continue
9104	  continue
        end if
c
c the above loops are about fourtimes faster than the original
c loop over all grid points for several reasons, the biggest being that
c we are only solving laplace's equation (unless salt is present), which
c numerically much simpler, hence faster. we put all we leave out, back
c in below, ending up with an equivalent calculation, but much faster.
c
c b+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if (iper(1)) then
c calculating first slice
c         star=1+igrid*(1+igrid)/2
c         fin=lat2*igrid*(igrid-2)+1
c         fin-star=igrid*(igrid-3)*(igrid+1)/2

          ix=1+igrid*lat2
          if(rionst.gt.0.0) then
            do n=1,(igrid-3)*lat2+1
              temp1 = phimap2(ix)+phimap2(ix-1+lat1)
              temp2 = phimap2(ix+lat1)+phimap2(ix-lat2)
              rtemp2=phimap2(ix+lat1+lat1)+phimap2(ix-lat2+lat1)
              temp3 = phimap2(ix+long1)+phimap2(ix-long2)
              rtemp3=phimap2(ix+long1+lat1)+phimap2(ix-long2+lat1)
              phimap1(ix)=.5*(phimap1(ix+lat1)+phimap1(ix))*om1+(temp1+
     &        .5*(temp2+temp3+rtemp2+rtemp3))*(sf1(ix)+sf1(ix+lat1))*.5
c now updating last slice
              phimap1(ix+lat1)=phimap1(ix)
              ix=ix+igrid
            end do
          else
            do n=1,(igrid-3)*lat2+1
              temp1 = phimap2(ix)+phimap2(ix-1+lat1)
              temp2 = phimap2(ix+lat1) + phimap2(ix-lat2)
              temp3 = phimap2(ix+long1) + phimap2(ix-long2)
              phimap1(ix) = phimap1(ix)*om1 + (temp1+temp2+temp3)*sixth
c now updating last slice
              phimap1(ix+lat1)=phimap1(ix)
              ix=ix+igrid
            end do
          end if

          star=(igrid+1)/2
          iy=(igrid*(igrid+1)/2) - igrid + 1
          fin=(igrid*(igrid-1)-2)/2
          do 9212 ix=star,fin
            iy=iy+igrid
            bndx1(ix)=phimap1(iy)
            bndx2(ix)=phimap1(iy+ihgd2)
9212      continue
        end if
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

c first we add back the dielectric boundary points, by recalculating them
c individually. note this is still vectorised by means of a gathering
c load by the compiler.
c
C$DIR NO_RECURRENCE 
        do 9010 k=1,icount2a
	  ix=idpos(k)
	  temp1=phimap2(ix-1)*db(1,k)+phimap2(ix)*db(2,k)
	  temp2=phimap2(ix-lat2)*db(3,k)+phimap2(ix+lat1)*db(4,k)
          temp3=phimap2(ix-long2)*db(5,k)+phimap2(ix+long1)*db(6,k)
          phimap1(ix)= phimap1(ix) + temp1+temp2+temp3
9010    continue
c
c Reset x boundary values altered in above loops.
        star=(igrid+1)/2
        iy=(igrid*(igrid+1)/2) - igrid +1
        fin=(igrid*(igrid-1)-2)/2
C$DIR NO_RECURRENCE
        do 9201 ix=star,fin
          iy=iy+igrid
          phimap1(iy)=bndx1(ix)
          phimap1(iy+ihgd2)=bndx2(ix)
9201    continue
c
c next we add back an adjustment to all the charged grid points due to
c the charge assigned. the compiler directive just reassures the vector
c compiler that all is well as far as recurrence is concerned, i.e. it
c would think there is a recurrence below, where as in fact there is none.
c

C$DIR NO_RECURRENCE 
        do 9011 k=1,icount1a
          temp=qval(k)
          ix=iqpos(k)
          phimap1(ix)=phimap1(ix) + temp
9011    continue
c
c if periodic boundary condition option
c force periodicity using wrap around update of boundary values:
c 2nd slice-->last
c last-1 slice-->first
c
c z periodicity
c
        if(iper(3)) then
          do 9013 iz = 1,(igrid-2)**2,2
	    temp1=bndz(iz)
	    temp2=temp1+idif1z
	    temp3=temp2+inc1za
	    temp4=temp1+inc1zb
	    itemp1=temp1
	    itemp2=temp2
	    itemp3=temp3
	    itemp4=temp4
c           iz=1  ===       iz=64
	    phimap1(itemp1)=phimap2(itemp2)
c           iz=65   ===      iz=2
	    phimap1(itemp3)=phimap2(itemp4)
9013      continue
        end if
        if(iper(6).and..false.) then
          sumdown=0.0
          sumup=0.0
          do iz = 1,(igrid-2)**2,2
            temp1=bndz(iz)
            temp2=temp1+idif1z
            temp4=temp1+inc1zb
            itemp2=temp2
            itemp4=temp4
            sumup=sumup+phimap2(itemp2)
            sumdown=sumdown+phimap2(itemp4)
          end do
          tmp=((igrid-2)**2+1)/2.
          sumup=sumup/tmp-vdropz
          sumdown=sumdown/tmp+vdropz
          do iz = 1,(igrid-2)**2,2
            temp1=bndz(iz)
            temp2=temp1+idif1z
            temp3=temp2+inc1za
            itemp1=temp1
            itemp3=temp3
            phimap1(itemp1)=sumup
            phimap1(itemp3)=sumdown
c           write(6,*)sumup,sumdown
          end do
        end if

c
c y periodicity
c
        if(iper(2)) then
          do 9015 iy = 1,(igrid-2)**2,2
	    temp1=bndy(iy)
	    temp2=temp1+idif1y
	    temp3=temp2+inc1ya
	    temp4=temp1+inc1yb
            itemp1=temp1
            itemp2=temp2
            itemp3=temp3
            itemp4=temp4
            phimap1(itemp1)=phimap2(itemp2)
            phimap1(itemp3)=phimap2(itemp4)
9015	  continue
        end if
c
	if(icheb) then
        call omalt(sf1,sf2,qval,db,sixth,2*i-1,om1,om2,spec,
     &   rionst,nhgp,icount1b,icount2b)
	end if
c
c Next update phimap2 using the new phimap1
c
        if(rionst.gt.0.0) then	
          do 8004 n = 2, igrid-1
	    star=sta2(n)
	    fin=fi2(n)
            do 8006 ix = star,fin
              temp1 = phimap1(ix)       + phimap1(ix+1)
              temp2 = phimap1(ix+lat2)  + phimap1(ix-lat1)
              temp3 = phimap1(ix+long2) + phimap1(ix-long1)
       	      phimap2(ix) =phimap2(ix)*om1+(temp1+temp2+temp3)*sf2(ix)
8006	    continue
8004	  continue
	else
          do 8104 n = 2, igrid-1
	    star=sta2(n)
	    fin=fi2(n)
            do 8106 ix = star,fin
              temp1 = phimap1(ix)       + phimap1(ix+1)
              temp2 = phimap1(ix+lat2)  + phimap1(ix-lat1)
              temp3 = phimap1(ix+long2) + phimap1(ix-long1)
              phimap2(ix) =phimap2(ix)*om1+(temp1+temp2+temp3)*sixth
8106	    continue
8104	  continue
	end if
c
c b+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        if (iper(1)) then
c calculating first slice
c         star=igrid+(1+igrid**2)/2
c         fin=(igrid-3)*igrid/2+((igrid-2)*igrid**2+1)/2
c         fin-star=igrid*(long1-igrid-2)

          ix=long2
          if(rionst.gt.0.0) then
            do n=1,long1-igrid-1
              ix=ix+igrid
              temp1 = phimap1(ix+lat1)  + phimap1(ix+1)
              temp2 = phimap1(ix+lat2)  + phimap1(ix-lat1)
              rtemp2 = phimap1(ix+lat2+lat1)  + phimap1(ix)
              temp3 = phimap1(ix+long2) + phimap1(ix-long1)
              rtemp3 = phimap1(ix+long2+lat1) + phimap1(ix-long1+lat1)
              phimap2(ix)=.5*(phimap2(ix+lat1)+phimap2(ix))*om1+(temp1+
     &        .5*(temp2+temp3+rtemp2+rtemp3))*(sf2(ix)+sf2(ix+lat1))*.5
c now updating last slice
              phimap2(ix+lat1)=phimap2(ix)
            end do
          else
            do n=1,long1-igrid-1
              ix=ix+igrid
              temp1 = phimap1(ix+lat1)  + phimap1(ix+1)
              temp2 = phimap1(ix+lat2)  + phimap1(ix-lat1)
              temp3 = phimap1(ix+long2) + phimap1(ix-long1)
              phimap2(ix)=phimap2(ix)*om1+(temp1+temp2+temp3)*sixth
c now updating last slice
              phimap2(ix+lat1)=phimap2(ix)
            end do
          end if

          star=(igrid+2)/2
          iy=(igrid*(igrid+2)/2) - igrid +1
          fin=(igrid*(igrid-1)-1)/2
          do 8212 ix=star,fin
            iy=iy+igrid
            bndx3(ix)=phimap2(iy)
            bndx4(ix)=phimap2(iy+ihgd2)
8212      continue
        end if
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

C$DIR NO_RECURRENCE 
        do 8010 k=icount2a+1,icount2b
          ix=idpos(k)
          temp1=phimap1(ix)*db(1,k)+phimap1(ix+1)*db(2,k)
          temp2=phimap1(ix-lat1)*db(3,k)+phimap1(ix+lat2)*db(4,k)
          temp3=phimap1(ix-long1)*db(5,k)+phimap1(ix+long2)*db(6,k)
          phimap2(ix)=phimap2(ix) + temp1+temp2+temp3
8010    continue

c reset x  boundary condition
c
        star=(igrid+2)/2
        iy=(igrid*(igrid+2)/2) - igrid +1
        fin=(igrid*(igrid-1)-1)/2
C$DIR NO_RECURRENCE
        do 8201 ix=star,fin
          iy=iy+igrid
          phimap2(iy)=bndx3(ix)
          phimap2(iy+ihgd2)=bndx4(ix)
8201    continue
c
C$DIR NO_RECURRENCE 
	do 8011 k=icount1a+1,icount1b
          temp=qval(k)
          ix=iqpos(k)
          phimap2(ix)=phimap2(ix) + temp
8011    continue
c
c z periodicity
c
        if(iper(3)) then
          do 8013 iz = 2,(igrid-2)**2,2
            temp1=bndz(iz)
            temp2=temp1+idif2z
            temp3=temp2+inc2za
            temp4=temp1+inc2zb
            itemp1=temp1
            itemp2=temp2
            itemp3=temp3
            itemp4=temp4
c           iz =1     ===  iz = 64
            phimap2(itemp1)=phimap1(itemp2)
c           iz = 65  ===   iz = 2
            phimap2(itemp3)=phimap1(itemp4)
8013      continue
        end if
        if(iper(6).and..false.) then
          sumdown=0.0
          sumup=0.0
          do iz = 2,(igrid-2)**2,2
            temp1=bndz(iz)
            temp2=temp1+idif2z
            temp4=temp1+inc2zb
            itemp2=temp2
            itemp4=temp4
            sumup=sumup+phimap1(itemp2)
            sumdown=sumdown+phimap1(itemp4)
          end do
          tmp=((igrid-2)**2-1)/2.
          sumup=sumup/tmp-vdropz
          sumdown=sumdown/tmp+vdropz
          do iz = 2,(igrid-2)**2,2
            temp1=bndz(iz)
            temp2=temp1+idif2z
            temp3=temp2+inc2za
            itemp1=temp1
            itemp3=temp3
            phimap2(itemp1)=sumup
            phimap2(itemp3)=sumdown
          end do
        end if
c
c y periodicity
c
        if(iper(2)) then
          do 8015 iy = 2,(igrid-2)**2,2
	    temp1=bndy(iy)
	    temp2=temp1+idif2y
	    temp3=temp2+inc2ya
	    temp4=temp1+inc2yb
            itemp1=temp1
            itemp2=temp2
            itemp3=temp3
            itemp4=temp4
            phimap2(itemp1)=phimap1(itemp2)
            phimap2(itemp3)=phimap1(itemp4)
8015      continue
        end if
c
	if(icheb) then
        call omalt(sf1,sf2,qval,db,sixth,2*i,om1,om2,spec,
     &  rionst,nhgp,icount1b,icount2b)
	end if
c
c we also save time by only checking convergence every ten
c iterations, rather than every single iteration.
c
	if(mod(i,icon1).eq.(icon1-1)) then
	do 8051 ix=2,(icgrid+1)/2,icon2
	  phimap3(ix)=phimap2(ix)
8051    continue
	end if
c
	if(gten.gt.0.0) then
	  grden=0.0
	  do ix=1,icount1a
	    iy=iqpos(ix)
	    grden=grden + phimap1(iy)*gval(ix)
	  end do
	  do ix=icount1a+1,icount1b
	    iy=iqpos(ix)
	    grden=grden+phimap2(iy)*gval(ix)
	  end do
c b++++++++++++modified++to save on grdn dimension++++++++++++
          ii=mod(i,5)
	  grdn(ii)=grden/2.0
	  if(i.gt.10) then
	    igt=.true.
	    do ix=1,5
	    do iy=1,5
	      if(abs(grdn(iy)-grdn(ix)).gt.gten) igt=.false.
	    end do
	    end do
	    if(igt)then
              write(6,*) (grdn(iy),iy=1,5)
	      ires=1
	    end if
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++
	  end if
c
	end if
c
	if((mod(i,icon1).eq.0).or.(ires.eq.1)) then
	  rnorm2=0
          do 8050 ix=2,(icgrid+1)/2,icon2
	    temp2=phimap3(ix)-phimap2(ix)
	    rnorm2=rnorm2+temp2**2
	    rmxch=amax1(rmxch,abs(temp2))
8050      continue
          rmsch = sqrt(float(icon2)*rnorm2/npoint)
          rnormch= sqrt(rnorm2)
	  rmsch2=rmsch
	  rmxch2=rmxch 
	  if(gten.gt.0.)then
	   write(6,*) rmsch2,rmxch2,grden,' at',i,' iterations'

	  else
	   write(6,*) rmsch2,rmxch2,' at',i,' iterations'
	  endif
c b++++++++changed and to or++++++++++++++++++++
          if(rmsch.le.res1.or.rmxch.le.res2.or.rnormch.le.res5) ires=1
c e+++++++++++++++++++++++++++++++++++++++++++++
	  if(igraph.and.(once)) then 
	    do 8053 j=i-9,i
	      ibin = (j-1.)*(nxran-1.)/(nlit-1.) + 1
	      rmsl(ibin) = rmsch
8053        rmaxl(ibin) = rmxch
	  end if
        end if
c
c
c check to see if accuracy is sufficient, or if a qstop command
c has been issued
c
c
      inquire(file='qstop.test',exist=qstopper)
          if(qstopper) ires=1
c
c LOOP
c
      i=i+1
c
      if (amax1(gten,res1,res2,res5).lt.1.e-6) then
c     if(gten.lt.1.e-6.and.res1.lt.1.e-6.and.res2.lt.1.e-6) then
	  if(i.le.nlit.and.ires.eq.0) goto 1000
      else
	  if((i.le.nlit.or.iautocon).and.ires.eq.0) goto 1000
      end if
c
c	end of iteration loop
c
c       remap into phimap
c
	do 8701 iy=1,(icgrid-1)/2 
	  ix=iy*2 
	  phimap3(ix-1)=phimap1(iy)
	  phimap3(ix)=phimap2(iy)
8701	continue 
	if(once) then
	  iw=1 
	  do 8801 iz=1,igrid
	    do 8802 iy=1,igrid
	      do 8803 ix=1,igrid
	         phimap(ix,iy,iz)=phimap3(iw)
	       iw=iw+1
8803	      continue
8802        continue
8801      continue
	  phimap(igrid,igrid,igrid)=phimap1((icgrid+1)/2)
	else
	  iw=1 
	  do 8881 iz=1,igrid
	    do 8882 iy=1,igrid
	      do 8883 ix=1,igrid
	       phimap(ix,iy,iz)=phimap(ix,iy,iz)-phimap3(iw)
	       iw=iw+1
8883	      continue
8882        continue
8881      continue
	phimap(igrid,igrid,igrid)=phimap(igrid,igrid,igrid)  
     &                          - phimap1((icgrid+1)/2)
	end if 
c ++da cacciare!!++++++++++++++++++++++++++++++++
        if (.false.) then
c         do iy=2,igrid-1
c         do iz=2,igrid-1
c            write(6,*)iy,iz,phimap(1,iy,iz),phimap(igrid,iy,iz)
c         end do
c         end do
c        open(52,file='potz',form='formatted')
c          do iy=1,igrid
c          do ix=1,igrid
c             write(52,*)phimap(ix,iy,1),phimap(ix,iy,igrid)
c          end do
c          end do
c        close(52)
        write(*,*)"pot111:",phimap(1,1,1)
        write(*,*)"pot112:",phimap(1,1,2)
        write(*,*)"pot113:",phimap(1,1,3)
        write(*,*)"pot123:",phimap(1,2,3)
        end if
c e++++++++++++++++++++++++++++++++++++++++++++++
c
	if(diff.and.(once)) then
	  write(6,*) 'now doing uniform dielectric run....'
	  once=.false.
	  om3= 2.0/(1 +(3.14159/float(igrid)))
	  sixth=sixth*om3/om2
	  do 8020 i=1,icgrid+1
	    phimap3(i)=phimap3(i)*epsrat 
8020      continue
	  do 8021 i=1,icount1b
	    qval(i)=qval(i)*om3/om2
8021	  continue 
	  do 8022 i=1,ibc
	    itemp=cgbp(5,i)
	    qval(itemp)=cgbp(4,i)*om3
8022	  continue 
	    om1=1-om3 
	    icount2a=0
	    icount2b=0
	    nlit=int(7.8*float(igrid)/3.14159)
	    i=1
	  goto 1689
	end if 
c
	icount2a=icount2abac
	icount2b=icount2bbac
c 
      finish = cputime(start)
      call datime(day)
	write(6,*)'finished qdiffx linear iterations'
	write(6,*)'at                       : ',day(12:19)
        write(6,*)'total time elapsed so far: ',finish
	write(6,*)'# loops                  : ',(i-1)
	write(6,*)'mean,max change (kT/e)   : ',rmsch2,rmxch2
c
c  plot convergence history   
c
	if(igraph) then
	iclr = 1
	iscl = 1
	imk = 0
	iplt = 0
	symb = 'M'
	title = '    linear iteration convergence history   '
	call conplt(rmaxl,title,iclr,iscl,imk,iplt,symb,1,nlit,
     1iplot,ymin,ymax)
	iclr = 0
	call conplt(rmsl,title,iclr,iscl,imk,iplt,symb,1,nlit,
     1iplot,ymin,ymax)
	iscl = 0
	imk = 1
	call conplt(rmaxl,title,iclr,iscl,imk,iplt,symb,1,nlit,
     1iplot,ymin,ymax)
	symb = 'A'
	iplt = 1
	call conplt(rmsl,title,iclr,iscl,imk,iplt,symb,1,nlit,
     1iplot,ymin,ymax)
	end if 
c
c code phimap corner, for use in transference from irises to convex
c and via versa
	ap1=phimap(1,1,1)
	ap2=ap1*10000
	ap3=float(int(ap2))
	if(ap3.gt.0) then
	ap4=(ap3+0.8)/10000
	else
	ap4=(ap3-0.8)/10000
	end if
	phimap(1,1,1)=ap4
c
	if(ipoten) then
	midg = (igrid+1)/2
	do 9034 m = 1,5
	  n = (igrid - 1)/4
	  nn = (m-1)*n + 1
	  write(6,*)'phi',nn,midg
	  write(6,*)(phimap(nn,midg,ii),ii=1,igrid)
9034	continue
	end if 

	return
	end
