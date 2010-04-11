	subroutine nitit(idpos,db,sf1,sf2,iqpos,qval,icount2a,icount2b,
     &	icount1a,icount1b,spec,nsp,phimap,phimap1,phimap2,phimap3,
     &	idebmap,bndx,bndy,bndz,bndx1,bndx2,bndx3,bndx4,
     &	qmap1,qmap2,debmap1,debmap2,idirectalg,qfact)
c
c
c NOTE THIS HAS BEEN ALTERED TO GIVE THE CONVERGENCE TO THE EXACT
C SOLUTION, WHICH IS INPUTTED VIA OPTION 3,(AND NOW WITH GAUSS
C SIEDEL IMPLEMENTED, WITH MAPPED SUBARRAYS.)
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
c
	parameter ( nxran = 60 )
	parameter ( nyran = 20 )
	dimension rmsl(nxran),rmsn(nxran),rmaxl(nxran),rmaxn(nxran)
	dimension qval(icount1b),qmap1(nhgp),qmap2(nhgp), debmap2(nhgp)
	dimension db(6,nsp),sf1(nhgp),sf2(nhgp),debmap1(nhgp)
        real phimap1(nhgp),phimap2(nhgp),phimap3(ngp)
        real phimap(igrid,igrid,igrid)
	logical*1 idebmap(igrid,igrid,igrid)
	integer*4 iqpos(icount1b),idpos(nsp)
        integer idirectalg
	dimension bndx1(nbgp),bndx2(nbgp),bndx3(nbgp),bndx4(nbgp)
	dimension bndx(nbgp),bndy(nbgp),bndz(nbgp)
	character*24 day
	character*1 symb
	character*70 title,iplot(nyran)
	logical qstopper,resdat
	integer star,fin,sta1(ngrid),sta2(ngrid),fi1(ngrid),fi2(ngrid)
c b+++++++++++++++++++++++++
        integer icont,icountplus,itshift
        logical ichangeom,inew,inewfirst,istop
        real conv(3),omcomp,tmp,der,relparprev,qfact,deb
        real factor,delom,linrelpar,cost
        character*18 nlstr
        character*24 fdate
        external fdate

        nlstr='                  '
        icountplus=0
        factor=1.0
        ichangeom=.true. 
        inewfirst=.false.
        istop=.true.
        inew=.true.
        itshift=0
c e+++++++++++++++++++++++++
	debfct = epsout/(deblen*scale)**2
        cost=debfct/(2.*rionst*epsout)
        npoint = (igrid-2)**3
c-------------------------------------------------------
        start = cputime(0.0)
        day=fdate()
        write(6,*)'now iterating at: ',day(12:19)
c-------------------------------------------------------
c
c some initialization
c
c b+++++++++++++++++++++++++++++++++++++++++++++++++++++
        conv(1)=0.0
        conv(2)=0.0
        conv(3)=0.0
c e++++++++++++++++++++++++++++++++++++++++++++++++++++

        tmp=abs(chi2*chi4)
        icont=0
	sixth = 1./6.
	icgrid=igrid**3
	ihgd=(igrid+1)/2
	if(icon2.eq.0) then
	mcon1=10
	icon2=1
	end if 
	itnum=0
	fraction=0.0 
	if(icon1.gt.nlit) icon1=nlit 
c
c       do 3030 ix=1,nhgp
c         qmap1(ix)=0.0 no longer needed, calloc superseded malloc
c         qmap2(ix)=0.0 no longer needed, calloc superseded malloc
c3030	continue 
	j=0
	do 3040 iz=1,igrid
	  do 3050 iy=1,igrid
	    do 3060 ix=1,igrid
	    j=j+1
            deb=0.
            if (idebmap(ix,iy,iz)) deb=1.
	    phimap3(j)=deb
3060	continue
3050	continue
3040	continue 
	do 3070 ix=1,nhgp
	iy=ix*2
	debmap1(ix)=phimap3(iy-1)
	debmap2(ix)=phimap3(iy)
3070	continue 
c 
	do 9000 i = 1,nxran
	  rmsl(i) = 0.0
	  rmsn(i) = 0.0
	  rmaxl(i) = 0.0
	  rmaxn(i) = 0.0
9000	continue
c
c comment out for cray version 14, nov 88, kas
c
c ---------------------------------------------
c MAIN SET UP ROUTINE	
c ---------------------------------------------
c
	if(iper(1)) then
	n=0
	do 440 iz=2,igrid-1
	  iadd1=(iz-1)*igrid*igrid 
	  do 441 iy=2,igrid-1
	    iadd2=(iadd1+(iy-1)*igrid +2)/2
	    n=n+1
	    bndx(n)=iadd2
441	  continue
440     continue
	idif1x=(igrid-2)/2
	idif2x=idif1x+1
	inc1xa=1
	inc1xb=0
	inc2xa=0
	inc2xb=1
	end if 
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
	if(iper(3)) then
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
c
c      inquire(file='res.dat',exist=resdat)
c      if(resdat) then
c        open(31,file='res.dat')
c        read(31,*,err=65) res1,res2
c          if(nnit.ne.0) then
c            read(31,*,err=55) res3,res4
c55        else
c            res3=0.0
c            res4=0.0
c          endif
c        close(31)
c65    else
c       res1=0.0
c       res2=0.0
c       res3=0.0
c      res4=0.0
c      end if
c	if(resdat) then 
c	write(6,*) ' '
c	write(6,*) 'linear resolution criteria are:',res1,res2
c	if(nnit.ne.0) then
c	write(6,*) 'non-linear resolution criteria are:',res3,res4
c	end if
c	write(6,*) ' '
c	end if 
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

      ires=0
c
	iw=1
	do 311 iz=1,igrid
	  do 312 iy=1,igrid
	    do 313 ix=1,igrid
	    iw=iw+1
	    phimap3(iw)=phimap(ix,iy,iz)
313         continue
312       continue
311     continue
	do 314 ix=2,icgrid+1,2
	iy=ix/2
	phimap1(iy)=phimap3(ix)
	phimap2(iy)=phimap3(ix+1)
314	continue
c
	star=(igrid+1)/2
	iy=(igrid*(igrid+1)/2) - igrid + 1
	fin=(igrid*(igrid-1)-2)/2
	ihgd2=ihgd-1
	do 9211 ix=star,fin
	  iy=iy+igrid
	  bndx1(ix)=phimap1(iy)
	  bndx2(ix)=phimap1(iy+ihgd2)
9211    continue
c 
	star=(igrid+2)/2
	iy=(igrid*(igrid+2)/2) - igrid +1
	fin=(igrid*(igrid-1)-1)/2
	do 8211 ix=star,fin
     	  iy=iy+igrid
	  bndx3(ix)=phimap2(iy)
	  bndx4(ix)=phimap2(iy+ihgd2)
8211    continue
c
	om2=2.0/(1.0 + sqrt(1 - spec))
        if (.not.imanual) ichangeom=.false.
        relparprev=om2
        linrelpar=om2
        write(6,*)'linear rel. parameter = ',linrelpar
        if (imanual) then
          write(6,*)'non linear fixed rel. parameter =',relpar 
        else
          write(6,*)'non linear initial rel. parameter =',relpar
          write(6,*)'q factor',qfact
        end if
	om1=1.0-om2

        write(6,*) ' '
        write(6,*) ' '
        write(6,*) '  rms-change     max change         #iterations'

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
	i=1
c

1000      continue
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
              temp1 = phimap2(ix)+phimap2(ix-1)
              temp2 = phimap2(ix+lat1)+phimap2(ix-lat2)
              temp3 = phimap2(ix+long1)+phimap2(ix-long2)
       	      phimap1(ix) =phimap1(ix)*om1 +(qmap1(ix) + temp1+temp2+
     &                     temp3)*sf1(ix)
c b++++++++++++++++++++++++++++++temporaneo?++++++++++++
c             if (debmap1(ix).eq.1.) then
c               maxphi=abs(phimap1(ix))
c               if (maxphi.gt.50) phimap1(ix)=phimap1(ix)*50/maxphi
c             end if 
c e++++++++++++++++++++++++++++temporaneo?**************
9006	    continue
9004	  continue
c
c otherwise the main loop is as below:
        else
          do 9104 n = 2, igrid-1
	    star=sta1(n)
	    fin=fi1(n)
            do 9106 ix = star,fin
              temp1 = phimap2(ix)+phimap2(ix-1)
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
c first we add back the dielectric boundary points, by recalculating them
c individually. note this is still vectorised by means of a gathering
c load by the compiler.
c
C$DIR NO_RECURRENCE 
c b+++++++++++++++++++
c       if ((idirectalg.ne.0).and.(rionst.eq.0.0)) then
c       do 9008 k=1,icount2a
c        ix=idpos(k)
c        temp1=phimap2(ix-1)*(db(1,k)-sixth)+phimap2(ix)*(db(2,k)-sixth)
c       temp2=phimap2(ix-lat2)*(db(3,k)-sixth)+phimap2(ix+lat1)*(db(4,k)
c    &  -sixth)
c       temp3=phimap2(ix-long2)*(db(5,k)-sixth)+phimap2(ix+long1)*(db(6,
c    &  k)-sixth)
c        phimap1(ix)= phimap1(ix) + temp1+temp2+temp3
c 9008    continue
c       else
c e+++++++++++++++++++
        do 9010 k=1,icount2a
	  ix=idpos(k)
	  temp1=phimap2(ix-1)*db(1,k)+phimap2(ix)*db(2,k)
	  temp2=phimap2(ix-lat2)*db(3,k)+phimap2(ix+lat1)*db(4,k)
          temp3=phimap2(ix-long2)*db(5,k)+phimap2(ix+long1)*db(6,k)
          phimap1(ix)= phimap1(ix) + temp1+temp2+temp3
9010    continue
c       end if
c
c next we add back an adjustment to all the charged grid points due to
c the charge assigned. the compiler directive just reassures the vector
c compiler that all is well as far as recurrence is concerned, i.e. it
c would think there is a recurrence below, where as in fact there is none.
c
c Now reset boundary values altered in above loops.
c 
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
            phimap1(itemp1)=phimap2(itemp2)
            phimap1(itemp3)=phimap2(itemp4)
9013      continue
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
c x periodicity
c
        if(iper(1)) then
          do 9017 ix = 1,(igrid-2)**2,2
	    temp1=bndx(ix)
	    temp2=temp1+idif1x
	    temp3=temp2+inc1xa
	    temp4=temp1+inc1xb
            itemp1=temp1
            itemp2=temp2
            itemp3=temp3
            itemp4=temp4
            phimap1(itemp1)=phimap2(itemp2)
            phimap1(itemp3)=phimap2(itemp4)
9017      continue
        end if
c
c Next update phimap2 using the new phimap1
c
        if(rionst.gt.0.0) then	
          do 8004 n = 2, igrid-1
	    star=sta2(n)
	    fin=fi2(n)
            do 8006 ix = star,fin
              temp1 = phimap1(ix)+ phimap1(ix+1)
              temp2 = phimap1(ix+lat2)+phimap1(ix-lat1)
              temp3 = phimap1(ix+long2) + phimap1(ix-long1)
	      phimap2(ix) =phimap2(ix)*om1 + (qmap2(ix)+temp1+temp2+
     &                     temp3)*sf2(ix)
c b++++++++++++++++++++++++++++++temporaneo?++++++++++++
c             if (debmap2(ix).eq.1.) then
c               maxphi=abs(phimap2(ix))
c               if (maxphi.gt.50) phimap2(ix)=phimap2(ix)*50/maxphi
c             end if
c e++++++++++++++++++++++++++++temporaneo?**************
8006	    continue
8004	  continue
	else
          do 8104 n = 2, igrid-1
	    star=sta2(n)
	    fin=fi2(n)
            do 8106 ix = star,fin
              temp1 = phimap1(ix)+phimap1(ix+1)
              temp2 = phimap1(ix+lat2) + phimap1(ix-lat1)
              temp3 = phimap1(ix+long2) + phimap1(ix-long1)
       	      phimap2(ix) =phimap2(ix)*om1 + (temp1+temp2+temp3)*sixth
8106	    continue
8104	  continue
	end if
c
C$DIR NO_RECURRENCE 
c b+++++++++++++++++++
c       if ((idirectalg.ne.0).and.(rionst.eq.0.0)) then
c       do 8008 k=icount2a+1,icount2b
c       ix=idpos(k)
c       temp1=phimap1(ix)*(db(1,k)-sixth)+phimap1(ix+1)*(db(2,k)-sixth)
c       temp2=phimap1(ix-lat1)*(db(3,k)-sixth)+phimap1(ix+lat2)*(db(4,k)
c    &  -sixth)
c       temp3=phimap1(ix-long1)*(db(5,k)-sixth)+phimap1(ix+long2)*(db(6,
c    &  k)-sixth)
c       phimap2(ix)=phimap2(ix) + temp1+temp2+temp3
c 8008    continue
c       else
c e+++++++++++++++++++
        do 8010 k=icount2a+1,icount2b
	  ix=idpos(k)
	  temp1=phimap1(ix)*db(1,k)+phimap1(ix+1)*db(2,k)
	  temp2=phimap1(ix-lat1)*db(3,k)+phimap1(ix+lat2)*db(4,k)
          temp3=phimap1(ix-long1)*db(5,k)+phimap1(ix+long2)*db(6,k)
          phimap2(ix)=phimap2(ix) + temp1+temp2+temp3
8010    continue
c       end if
c reset boundary condition
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
            phimap2(itemp1)=phimap1(itemp2)
            phimap2(itemp3)=phimap1(itemp4)
8013      continue
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
8015	  continue
        end if
c
c x periodicity
c
        if(iper(1)) then
          do 8017 ix = 2,(igrid-2)**2,2
	    temp1=bndx(ix)
	    temp2=temp1+idif2x
	    temp3=temp2+inc2xa
	    temp4=temp1+inc2xb
            itemp1=temp1
            itemp2=temp2
            itemp3=temp3
            itemp4=temp4
            phimap2(itemp1)=phimap1(itemp2)
            phimap2(itemp3)=phimap1(itemp4)
8017      continue
         end if
c
c we also save time by only checking convergence every ten
c iterations, rather than every single iteration.
c
c store phi2 in phi3 to compare against next iteration
	if(mod(i,icon1).eq.(icon1-1)) then
	do 8051 ix=2,(icgrid+1)/2,icon2
	  phimap3(ix)=phimap2(ix)
8051    continue
	end if
c
c check convergence
	if(mod(i,icon1).eq.0) then
c rmsch= rms change
c store in rmsch2
c rmxch= max change
c store in rmxch2
	  rmsch2=rmsch
          rmxch2=rmxch 
c
	  rnorm2=0
	  if(icon2.ne.1) then
            do ix=2,(icgrid+1)/2,icon2
              temp2=phimap3(ix)-phimap2(ix)
              rnorm2=rnorm2+temp2**2
	      rmxch=amax1(rmxch,abs(temp2))
	    end do
	  end if
	  if(icon2.eq.1) then
            do ix=2,(icgrid+1)/2
	      temp2=phimap3(ix)-phimap2(ix)
	      rnorm2=rnorm2+temp2**2
	      rmxch=amax1(rmxch,abs(temp2))
	    end do
	  end if
c b+++++++++++++++++++++++++++++++++++++++++++++++++++++++
          conv(3)=conv(2)
          conv(2)=conv(1)
          conv(1)=rmxch
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++
c
          rmsch = sqrt(float(icon2)*rnorm2/npoint)
          rnormch=sqrt(rnorm2)/relpar

c b+++++++++++++++++++++++++++++++++++
            if((rmsch.le.res1.or.rmxch.le.res2.or.rnormch.le.res5).and.
     &          itnum.gt.22) ires=1
c e+++++++++++++++++++++++++++++++++++

	  if(itnum.eq.0) then 
	    write(6,*) rmsch,rmxch,' at ',i,'iterations'
            istop=.not.(rmxch.ge.0.22)
	    if(igraph) then 
	      do 8053 j=i-9,i
	        ibin = (j-1.)*(nxran-1.)/(nlit-1.) + 1
	        rmsl(ibin) = rmsch
8053            rmaxl(ibin) = rmxch
	    end if 
c b+++++++++++++++++++++++++++++++++++++
c ottimizzazione di primo passo
            inewfirst=(i.ge.nlit-mod(nlit,icon1).and.istop.and.
     &itnum.eq.0)
            if (.not.imanual.and.inewfirst.and.qfact.gt.3.2) then
              factor=exp(-qfact*2.1)+1.E-6
              ichangeom=.true.
            end if
	  end if 

c nonlinear part
          inew=inew.or.inewfirst
          if (itnum.ne.0.) then
	    write(6,*) rmsch,rmxch,itnum,'it. ',nlstr
            if (.not.imanual) then
              derprec=der
              der=(conv(1)-conv(2))/conv(1)
              if(rmxch.lt.1.e-6) then
                factor=1.2
                ichangeom=.true.
              else  
                if (der.gt.0..and.(.not.inew)) then
                  icountplus=icountplus+1
                  factor=factor*(1.-der)**.99
c                 write(6,*)'factor:',factor
                  if (der.gt.0.55) then
                    ichangeom=.true.
                    if (der.ge.1.) factor=1.e-5
                  end if
                  if(der.gt.0.35.and.conv(1).gt..1)then
                    ichangeom=.true.
                    factor=(factor*.05/conv(1))**4
                  end if
                end if
                if ((der.gt.0.and.conv(1).gt..1).and.inew.and..not.
c               if ((der.gt.0.and.conv(1).gt..1).and..not.inew.and..not.
     &inewfirst) then
                  ichangeom=.true.
              factor=amin1((factor*.05/conv(1)),factor*(1.-der)**.86)
                end if
                if (der.le.0.) then
                   icountplus=0
c                  write(6,*)'fatto',relpar,itnum,der,derprec
                   factor=1.
                   if (itnum.gt.24.and.itnum.lt.24+.75*(nnit-24).and.
     &rmxch.lt..03.and.derprec.le.0.) then
                     if(der.gt.-.2.and.derprec.gt.-.2) then
                       write(6,*)'                   Trying to speed up
     &the convergence process'
                       factor=1.1
                       ichangeom=.true.
                       if(relpar.lt..2.and.der.gt.-.05.and.derprec.gt.
     &-.05) factor=1-45.226*(relpar-.2)
                     end if
                   end if
                end if
                if (icountplus.ge.2) ichangeom=.true.
c               write(6,*) 'der:',der
              end if 
              inewfirst=.false.
            end if
c e++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	  end if
c
c end of convergence check
        end if
c
c check to see if accuracy is sufficient, or if a qstop command
c has been issued
ccommented out qstopper as obsoleteinquire(file='qstop.test',exist=qstopper)
c          if(qstopper) ires=1
c
c LOOP
c
      i=i+1
c b++++++++++++++++++++++++++++++++++++++++++++
      if((i.le.nlit.or..not.istop).and.ires.eq.0)  goto 1000
c e++++++++++++++++++++++++++++++++++++++++++++
c
c	end of iteration loop
c
c first pass write header
	if(nnit.gt.0.and.itnum.eq.0) then
	  write(6,*) ' '
	  write(6,*) 'now for the non-linear iterations'
	  write(6,*) ' '
	  write(6,*) '  rms-change     max change         #iterations'
	end if 
c
c icon1 = ogni quanti blocchi di iterazioni verifica convergenza
c nlit = quante iterazioni nel blocco 
c b+++OCT 2000
          icon1=10
          nlit=10
c e+++++++++++++
	itnum=itnum+1
	if(itnum.gt.nnit.or.ires.eq.1.and..not.inew) goto 9090 
        i=1
c b++++++++OCT 2000++++++++++++++++++++++++
        inew=ichangeom
        if (ichangeom) then
          relpar=relpar*factor
          if (relpar.lt.1.E-4) then
            write(6,*)'estimation ',relpar,' 1E-4 preferred'
            relpar=1.E-4
          end if
          factor=1.
          write(6,*)'                   New relaxation parameter =    '
     &,relpar
          ichangeom=.false.
          icountplus=0
          omcomp=relpar/relparprev
          relparprev=relpar
          om1=1.0-relpar
          do 901 ix=1,(icgrid+1)/2
            sf1(ix)=sf1(ix)*omcomp
            sf2(ix)=sf2(ix)*omcomp
901       continue
          do 902 ix=1,icount1b
            qval(ix)=qval(ix)*omcomp
902       continue
          do 903 iy=1,6
            do 904 ix=1,icount2b
               db(iy,ix)=db(iy,ix)*omcomp
904          continue
903       continue
          sixth=sixth*omcomp
          icont=icont+1
        end if

	fraction= fraction + 0.05
	if(fraction.gt.1.0) then
          fraction=1.0
          nlstr='full non-linearity'
        end if
c       write(6,*)'fra',fraction

c	fac1=fraction*debfct/(2.*rionst*epsout)
        fac1=fraction*cost
        if (tmp.lt.1.e-6) then
          do 8080 ix=1,nhgp
            temp1=phimap1(ix)*debmap1(ix)
            temp2=phimap2(ix)*debmap2(ix)
            temp3=temp1**2
            temp4=temp2**2
            qmap1(ix)=fac1*temp3*temp1*(chi3 + temp3*chi5)
            qmap2(ix)=fac1*temp4*temp2*(chi3 + temp4*chi5)
c b++++soglia messa per incrementare stabilita' della convergenza
            if(temp3.gt.2500) qmap1(ix)=0.
            if(temp4.gt.2500) qmap2(ix)=0.
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
c           qmap2(ix)=fac1*(-2.*rionst*(sinh(temp2)-temp2))
8080      continue
        else
	  do 7070 ix=1,nhgp
	    temp1=phimap1(ix)*debmap1(ix)
	    temp2=phimap2(ix)*debmap2(ix)
	    temp3=temp1**2
	    temp4=temp2**2
 	    qmap1(ix)=fac1*temp3*(chi2+temp1*(chi3 + temp1*(chi4+temp1*
     &              chi5)))
            qmap2(ix)=fac1*temp4*(chi2+temp2*(chi3 + temp2*(chi4+temp2*
     &              chi5)))
c b++++soglia messa per incrementare stabilita' della convergenza
            if(temp3.gt.2500) qmap1(ix)=0.
            if(temp4.gt.2500) qmap2(ix)=0.
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

c e+++++++++++++++++++++++++
7070	  continue
        end if
c now go do a couple of linear iterations
	goto 1000
c
9090	do 8701 iy=1,(icgrid-1)/2 
	  ix=iy*2 
	  phimap3(ix)=phimap2(iy)
	  phimap3(ix-1)=phimap1(iy)
8701	continue 
	iw=1 
	do 8801 iz=1,igrid
	  do 8802 iy=1,igrid
	    do 8803 ix=1,igrid
	       phimap(ix,iy,iz)=phimap3(iw)
	     iw=iw+1
8803	    continue
8802      continue
8801    continue
	phimap(igrid,igrid,igrid)=phimap1((icgrid+1)/2)
c
c b++++++++++++++++++++++++++++++++++++++++++++
      if (relpar.lt.0.05) then
         write(6,*)
     &   'Convergence is more reliable if relaxation parameter>0.05'
         write(6,*)
     &   'If it is possible, it is advisable to increase it'
         write(6,*)''
      end if
c e++++++++++++++++++++++++++++++++++++++++++++
c ++da cacciare!!++++++++++++++++++++++++++++++++
c       if (.false.) then
c       open(52,file='nlbound',form='formatted')
c         do ix=1,igrid
c            write(52,*)phimap(ix,(igrid+1)/2,(igrid+1)/2)
c         end do
c       close(52)

c       end if
c e++++++++++++++++++++++++++++++++++++++++++++++

        finish = cputime(start)
        call datime(day)
	write(6,*)'finished qdiffx linear iterations'
	write(6,*)'at                       : ',day(12:19)
        write(6,*)'time taken (sec)         : ',finish
	write(6,*)'# full non-linear loops  : ',(i-1)
c       write(6,*)'mean,max change (kT/e)   : ',rmsch2,rmxch2
        write(6,*)'mean,max change (kT/e)   : ',rmsch,rmxch
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
c	give some intermediate output of phi
c
	if(ipoten) then
	  midg = (igrid+1)/2
	  do 9034 m = 1,5
	    n = (igrid - 1)/4
	    nn = (m-1)*n + 1
	    write(6,*)'phi',nn,midg
	    write(6,*)(phimap(nn,midg,ii),ii=1,igrid)
9034	  continue
	end if 
	return
	end
