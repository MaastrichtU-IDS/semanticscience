	subroutine setbc(qplus,qmin,cqplus,cqmin,nqass,natom,ibnum)
c
c assigns either zero boundary conditions (ibctyp=1)
c quasi-coulombic based on debye dipole qplus at cqplus
c and qmin at cqmin (ibctyp=2)
c focussing (ibctyp=3)(continuance if scales are the same)
c full quasi-coulombic (ibctyp=4)
c or constant external field (ibctyp=5)
c option 2 will be appropriately modified by periodic
c boundary condition flags (iper)
c--------------------------------------------------------------
	include 'qdiffpar4.h'
	include 'qlog.h'
c--------------------------------------------------------------
	real phimap(igrid,igrid,igrid)
      real atmcrg(4,nqass)
	dimension cqplus(3),cqmin(3),g(3),go(3),c(3)
	character*20 toblbl
	character*10 label
	character*60 title
	character*80 filnam
	character*16 botlbl
c--------------------------------------------------------------
        integer ibnum
        logical*1 idebmap(igrid,igrid,igrid)
        real scspos(3,ibnum)
        real cqnet(3),tmp,cqnetA(3)
        h=1./scale
        ergestout=0.0
c
c zero option, clear boundary values
c
	write(6,*) " "
	write(6,*) "  setting boundary conditions"
	write(6,*) " "
c
c       goff = (igrid + 1.)/2.
c       eps2=1.
c       eps1=80
c       co=1.*561/eps2
c       d=3

c       write(6,*)'assigning suitable boundary conditions..',co
        do 9000 iz=1,igrid
          do 9002 ix=1,igrid,igrid-1
            do 9001 iy=1,igrid
               phimap(ix,iy,iz) = 0.0
9001        continue
9002	  continue
9000	continue
        do 9003 iz=1,igrid
          do 9004 iy=1,igrid,igrid-1
            do 9005 ix=1,igrid
              phimap(ix,iy,iz) = 0.0
9005	    continue
9004	  continue
9003	continue
        do 9006 iz=1,igrid,igrid-1
          do 9007 iy=1,igrid
            do 9008 ix=1,igrid
              phimap(ix,iy,iz) = 0.0
9008	    continue
9007	   continue
9006	 continue
c
c end of zero option
c
      if(ibctyp.eq.6.and.(.not.(logions.and.nnit.eq.0.and.qnet.ne.0.)))
     &   ibctyp=2

      if(ibctyp.eq.2) then
c
c quasi coulombic dipole option
c
        qnet=qmin+qplus
        do 9009 iz=1,igrid
        do 9010 iy=1,igrid
          dist1 = (cqplus(1)-1)**2 + (cqplus(2)-iy)**2
     &          + (cqplus(3)-iz)**2
          dist1 = sqrt(dist1)/scale
          tempp = qplus*exp(-dist1/deblen )/(dist1*epsout) 
          dist2 = (cqmin(1)-1)**2 + (cqmin(2)-iy)**2
     &          + (cqmin(3)-iz)**2
          dist2 = sqrt(dist2)/scale
          tempn = qmin*exp(-dist2/deblen )/(dist2*epsout) 
          phimap(1,iy,iz) =  tempp + tempn
          dist3 = (cqplus(1)-igrid)**2 + (cqplus(2)-iy)**2
     &          + (cqplus(3)-iz)**2
          dist3 = sqrt(dist3)/scale
          tempp = qplus*exp(-dist3/deblen )/(dist3*epsout) 
          dist4 = (cqmin(1)-igrid)**2 + (cqmin(2)-iy)**2
     &          + (cqmin(3)-iz)**2
          dist4 = sqrt(dist4)/scale
          tempn = qmin*exp(-dist4/deblen )/(dist4*epsout) 
          phimap(igrid,iy,iz) =  tempp + tempn
9010    continue
9009    continue
        do 9012 iz=1,igrid
        do 9013 iy=1,igrid,igrid-1
        do 9014 ix=1,igrid
          dist = (cqplus(1)-ix)**2 + (cqplus(2)-iy)**2
     &         + (cqplus(3)-iz)**2
          dist = sqrt(dist)/scale
          tempp = qplus*exp(-dist/deblen )/(dist*epsout) 
          dist = (cqmin(1)-ix)**2 + (cqmin(2)-iy)**2
     &         + (cqmin(3)-iz)**2
          dist = sqrt(dist)/scale
          tempn = qmin*exp(-dist/deblen )/(dist*epsout) 
          phimap(ix,iy,iz) =  tempp + tempn
9014    continue
9013    continue
9012    continue
        do 9015 iz=1,igrid,igrid-1
        do 9016 iy=1,igrid
        do 9017 ix=1,igrid
          dist = (cqplus(1)-ix)**2 + (cqplus(2)-iy)**2
     &         + (cqplus(3)-iz)**2
          dist = sqrt(dist)/scale
          tempp = qplus*exp(-dist/deblen )/(dist*epsout) 
          dist = (cqmin(1)-ix)**2 + (cqmin(2)-iy)**2
     &         + (cqmin(3)-iz)**2
          dist = sqrt(dist)/scale
          tempn = qmin*exp(-dist/deblen )/(dist*epsout) 
          phimap(ix,iy,iz) = tempp + tempn
9017    continue
9016    continue
9015    continue
      end if 
c
c end of quasi coulombic dipole option
c
      if(ibctyp.eq.7.and.(.not.(logions.and.nnit.eq.0.and.qnet.ne.0.)))
     &   ibctyp=4

      if(ibctyp.eq.4) then
c
c a summation of the potential resulted from each point of charge 
c
        qnet=qmin+qplus
	  do 9034 iz=1,igrid
	  do 9035 iy=1,igrid
	  do 9036 ix=1,igrid,igrid-1
	  do 9037 ic = 1,nqass
          dist = (atmcrg(1,ic)-ix)**2 + (atmcrg(2,ic)-iy)**2
     &         + (atmcrg(3,ic)-iz)**2
 	    dist = sqrt(dist)/scale
	    tempd = atmcrg(4,ic)*exp(-dist/deblen)/(dist*epsout)
          phimap(ix,iy,iz) = phimap(ix,iy,iz) + tempd 
9037 	  continue
9036	  continue
9035    continue
9034    continue
	  do 9038 iz=1,igrid
	  do 9039 iy=1,igrid,igrid-1
	  do 9040 ix=1,igrid
	  do 9041 ic = 1,nqass
          dist = (atmcrg(1,ic)-ix)**2 + (atmcrg(2,ic)-iy)**2
     &         + (atmcrg(3,ic)-iz)**2
 	    dist = sqrt(dist)/scale
	    tempd = atmcrg(4,ic)*exp(-dist/deblen)/(dist*epsout)
          phimap(ix,iy,iz) = phimap(ix,iy,iz) + tempd 
9041	  continue
9040	  continue
9039    continue
9038    continue
	  do 9042 iz=1,igrid,igrid-1
	  do 9043 iy=1,igrid
	  do 9044 ix=1,igrid
	  do 9045 ic = 1,nqass
          dist = (atmcrg(1,ic)-ix)**2 + (atmcrg(2,ic)-iy)**2
     &         + (atmcrg(3,ic)-iz)**2
 	    dist = sqrt(dist)/scale
	    tempd = atmcrg(4,ic)*exp(-dist/deblen)/(dist*epsout)
          phimap(ix,iy,iz) = phimap(ix,iy,iz) + tempd 
9045	  continue
9044	  continue
9043    continue
9042    continue
      end if 
c
c end of the option for the complete summation of potential
c
c
      if(ibctyp.eq.3) then
c 
c focussing option-bc's come from a previous phimap
c
	open(18,file=phiinam(:phiilen),status='old',
     1err=900,form='unformatted')
	write(6,*)' '
	write(6,*)'focussing boundary condition '
	write(6,*)'read from file'
	write(6,*)phiinam(:phiilen)
	write(6,*)' '
c
c read in old potential map
c
	read(18)toblbl
      read(18)label,title
      read(18)phimap
      read(18)botlbl
	read(18)scale1,oldmid1,igrid1
	close(18)
c check to see if this is a continuence
	
	if(scale1.eq.scale) then
	write(6,*) 'scales are the same.' 
	write(6,*) 'therefore assuming this to be a continuence'
	goto 511
	endif
	write(6,*)' '
      write(6,*)' focussing potential map:'
	write(6,200)title
	write(6,*)'original scale (grids/A)      : ',scale1
	write(6,*)'object centre at (A) : ',oldmid1
	write(6,*)' '
200	format(A60)
c
c check to see that new grid lies within old one that is going to
c provide bc's
c
      iout = 0
c	goff = (ngrid+1.)/2.
	goff = (igrid1+1.)/2.
	do 9018 iz=1,igrid,igrid-1
        g(3) = iz
	  do 9019 iy=1,igrid,igrid-1
          g(2) = iy
	    do 9020 ix=1,igrid,igrid-1
            g(1) = ix
c
c for each new grid corner, calculate old grid coords
c
            call gtoc(g,c)
            do 9021 i = 1,3
		  gold = (c(i) - oldmid1(i))*scale1 + goff
c line below replace 9/16/91 cos i think it should be between
c 1 and ngrid, not 2 and ngrid-1
c             if((gold.le.2.).or.(gold.ge.ngrid-1.))  iout = 1
c             if((gold.le.1).or.(gold.ge.ngrid))  iout = 1
              if((gold.le.1).or.(gold.ge.igrid1))  iout = 1
9021		continue
9020	    continue
9019	  continue
9018	continue
      if(iout.ne.0) then
	  write(6,*)'part of new grid lies outside old grid'
	  write(6,*)'check scaling of both grids'
	  write(6,*)'old scale:'
	  write(6,*)'scale (grids/A)      : ',scale1
	  write(6,*)'object centre at (A) : ',oldmid1
	  write(6,*)'new scale:'
	  write(6,*)'scale (grids/A)      : ',scale
	  write(6,*)'object centre at (A) : ',oldmid
	  stop
      end if
c
c for each boundary point
c convert to real coordinates
c convert to old grid coordinates
c interpolate potential
c note that can use same potential array for boundaries
c since old potentials at boundary are not used for new ones
c
c
c save new grid size, and set temporarily to 65
c
	isgrid = igrid
c	igrid = ngrid
	igrid = igrid1
	gmid = (isgrid + 1.)/2.
      write(6,*)'pulling boundary values out of old potential map...'
	do 9022 iz=2,isgrid-1
        g(3) = iz
	  do 9023 iy=2,isgrid-1
          g(2) = iy
	    do 9024 ix=1,isgrid,isgrid-1
            g(1) = ix
c
c for each new grid side, calculate old grid coords
c
		do 9025 i = 1,3
		  c(i) = (g(i) - gmid)/scale + oldmid(i)
		  go(i) = (c(i) - oldmid1(i))*scale1 + goff

9025		continue
c
c find potential
c
            call phintp(go,phiv)
            phimap(ix,iy,iz) = phiv

9024		    continue
9023		 continue
9022	    continue

	do 9026 iz=2,isgrid-1
        g(3) = iz
	  do 9027 iy=1,isgrid,isgrid-1
          g(2) = iy
	    do 9028 ix=2,isgrid-1
            g(1) = ix
c
c for each new grid side, calculate old grid coords
c
		do 9029 i = 1,3
		  c(i) = (g(i) - gmid)/scale + oldmid(i)
		  go(i) = (c(i) - oldmid1(i))*scale1 + goff
9029		continue
c
c find potential
c
            call phintp(go,phiv)
            phimap(ix,iy,iz) = phiv

9028		    continue
9027		 continue
9026	    continue

	do 9030 iz=1,isgrid,isgrid-1
        g(3) = iz
	  do 9031 iy=2,isgrid-1
          g(2) = iy
	    do 9032 ix=2,isgrid-1
            g(1) = ix
c
c for each new grid side, calculate old grid coords
c
		do 9033 i = 1,3
		  c(i) = (g(i) - gmid)/scale + oldmid(i)
		  go(i) = (c(i) - oldmid1(i))*scale1 + goff
9033		continue
c
c find potential
c
            call phintp(go,phiv)
            phimap(ix,iy,iz) = phiv
c
9032		    continue
9031		 continue
9030	    continue
c restore new grid size
c
	igrid = isgrid
511   end if 
c
c end of focussing option
c
      if(ibctyp.eq.5) then
        do 9051 iy=1,igrid
        do 9052 ix=1,igrid
          phimap(ix,iy,igrid) = vdropz
9052    continue
9051    continue
	end if
c
c end external field option
c
      if(ibctyp.eq.6) then
c
c quasi coulombic modified dipole option
c
        qnet=qmin+qplus
c b+++++++++++++++++++++++++++++++++++++++++++++++++++++
        i=2
        if (qmin.eq.0.or.qplus.eq.0) i=1
        goff=(igrid+1.)/2.
        cqnet(1)=(cqmin(1)+cqplus(1))/i
        cqnet(2)=(cqmin(2)+cqplus(2))/i
        cqnet(3)=(cqmin(3)+cqplus(3))/i
        cqnetA(1)=(cqnet(1)-goff)/scale+oldmid(1)
        cqnetA(2)=(cqnet(2)-goff)/scale+oldmid(2)
        cqnetA(3)=(cqnet(3)-goff)/scale+oldmid(3)
c     calcolo  raggio medio molecola
        tmp=0.
        do i=1,ibnum
          tmp=tmp+(scspos(1,i)-cqnetA(1))**2+(scspos(2,i)-cqnetA(2))**2
	    tmp=tmp+(scspos(3,i)-cqnetA(3))**2
        end do
  	  radius=sqrt(tmp/ibnum)+exrad
 
        ergestemp=0.0
c setting bc and calculating direct ionic contribution
        do 9109 iz=1,igrid
          cutedgesz=-2.5
          if (iz.eq.1.or.iz.eq.igrid) cutedgesz=2.
          do 9110 iy=1,igrid
            cutedges=cutedgesz
            if (iy.eq.1.or.iy.eq.igrid) cutedges=cutedgesz+1
            dist1=1-cqplus(1)
            dist=dist1**2+(cqplus(2)-iy)**2+(cqplus(3)-iz)**2
            dist=sqrt(dist)/scale
            tempp = qplus*exp(-dist/deblen)/(dist*epsout)
            dist1=1-cqmin(1)
            dist=dist1**2+(cqmin(2)-iy)**2+(cqmin(3)-iz)**2
            dist =sqrt(dist)/scale
            tempn = qmin*exp(-dist/deblen )/(dist*epsout)
            phimap(1,iy,iz) =  tempp + tempn

            dist1=igrid-cqplus(1)
            dist =dist1**2+(cqplus(2)-iy)**2+(cqplus(3)-iz)**2
            dist = sqrt(dist)/scale
            tempp = qplus*exp(-dist/deblen )/(dist*epsout)
            dist1=igrid-cqmin(1)
            dist =dist1**2+(cqmin(2)-iy)**2+(cqmin(3)-iz)**2
            dist = sqrt(dist)/scale
            tempn = qmin*exp(-dist/deblen )/(dist*epsout)
            phimap(igrid,iy,iz) =  tempp + tempn

            dist1=1-cqnet(1)
            dist =dist1**2+(cqnet(2)-iy)**2+(cqnet(3)-iz)**2
	      dist = sqrt(dist)/scale
            fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
	      dist1=dist1*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
	      ergestemp=ergestemp+qnet*tempd*dist1/dist**2

            dist1=igrid-cqnet(1)
            dist =dist1**2+(cqnet(2)-iy)**2+(cqnet(3)-iz)**2
	      dist = sqrt(dist)/scale
	      fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
            dist1=dist1*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
            ergestemp=ergestemp-qnet*tempd*dist1/dist**2

9110      continue
9109    continue
        if (.not.iper(1)) ergestout=ergestout+ergestemp

        ergestemp=0.0
        do 9112 iz=1,igrid
          cutedgesz=-2.5
          if (iz.eq.1.or.iz.eq.igrid) cutedgesz=2.
          do 9114 ix=1,igrid
            cutedges=cutedgesz
            if (ix.eq.1.or.ix.eq.igrid) cutedges=cutedgesz+1
            dist2=1-cqplus(2)
            dist=(cqplus(1)-ix)**2+dist2**2+(cqplus(3)-iz)**2
            dist = sqrt(dist)/scale
            tempp = qplus*exp(-dist/deblen)/(dist*epsout)
            dist2=1-cqmin(2)
            dist=(cqmin(1)-ix)**2+dist2**2+(cqmin(3)-iz)**2
            dist = sqrt(dist)/scale
            tempn = qmin*exp(-dist/deblen )/(dist*epsout)
            phimap(ix,1,iz) =  tempp + tempn

            dist2=igrid-cqplus(2)
            dist=(cqplus(1)-ix)**2+dist2**2+(cqplus(3)-iz)**2
            dist = sqrt(dist)/scale
            tempp = qplus*exp(-dist/deblen)/(dist*epsout)
            dist2=igrid-cqmin(2)
            dist=(cqmin(1)-ix)**2+dist2**2+(cqmin(3)-iz)**2
            dist = sqrt(dist)/scale
            tempn = qmin*exp(-dist/deblen )/(dist*epsout)
            phimap(ix,igrid,iz) =  tempp + tempn

            dist2=1-cqnet(2)
            dist =dist2**2+(cqnet(1)-ix)**2+(cqnet(3)-iz)**2
 	      dist = sqrt(dist)/scale
            fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
	      dist2=dist2*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
	      ergestemp=ergestemp+qnet*tempd*dist2/dist**2
            dist2=igrid-cqnet(2)
            dist =dist2**2+(cqnet(1)-ix)**2+(cqnet(3)-iz)**2
	      dist = sqrt(dist)/scale
	      fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
            dist2=dist2*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
            ergestemp=ergestemp-qnet*tempd*dist2/dist**2

9114      continue
9112    continue
        if (.not.iper(2)) ergestout=ergestout+ergestemp
        ergestemp=0.0
        do 9116 iy=1,igrid
          cutedgesy=-2.5
          if (iy.eq.1.or.iy.eq.igrid) cutedgesy=2.
          do 9117 ix=1,igrid
            cutedges=cutedgesy
            if (ix.eq.1.or.ix.eq.igrid) cutedges=cutedgesy+1
            dist3=1-cqplus(3)
            dist=(cqplus(1)-ix)**2+(cqplus(2)-iy)**2+dist3**2
            dist = sqrt(dist)/scale
            tempp = qplus*exp(-dist/deblen )/(dist*epsout)
            dist3=1-cqmin(3)
            dist=(cqmin(1)-ix)**2+(cqmin(2)-iy)**2+dist3**2
            dist = sqrt(dist)/scale
            tempn = qmin*exp(-dist/deblen )/(dist*epsout)
            phimap(ix,iy,1) = tempp + tempn

            dist3=igrid-cqplus(3)
            dist=(cqplus(1)-ix)**2+(cqplus(2)-iy)**2+dist3**2
            dist = sqrt(dist)/scale
            tempp = qplus*exp(-dist/deblen )/(dist*epsout)
            dist3=igrid-cqmin(3)
            dist=(cqmin(1)-ix)**2+(cqmin(2)-iy)**2+dist3**2
            dist = sqrt(dist)/scale
            tempn = qmin*exp(-dist/deblen )/(dist*epsout)
            phimap(ix,iy,igrid) = tempp + tempn

            dist3=1-cqnet(3)
            dist =dist3**2+(cqnet(2)-iy)**2+(cqnet(1)-ix)**2
	      dist = sqrt(dist)/scale
            fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
	      dist3=dist3*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
	      ergestemp=ergestemp+qnet*tempd*dist3/dist**2
            dist3=igrid-cqnet(3)
            dist =dist3**2+(cqnet(2)-iy)**2+(cqnet(1)-ix)**2
	      dist = sqrt(dist)/scale
	      fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
            dist3=dist3*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
            ergestemp=ergestemp-qnet*tempd*dist3/dist**2

9117      continue
9116    continue
        if (.not.iper(3)) ergestout=ergestout+ergestemp

        ergestout=ergestout*rionst*deblen*.0006023/(epsout*scale**3)
      end if 
c
c end of quasi coulombic modified dipole option

      if(ibctyp.eq.7) then
c a summation of the potential resulted from each point of charge 
c
        qnet=qmin+qplus
c here sets bc and calculates ionic direct contribution at the same time
	  i=2
	  if (qmin.eq.0.or.qplus.eq.0) i=1
	  goff=(igrid+1.)/2.
        cqnet(1)=(cqmin(1)+cqplus(1))/i
        cqnet(2)=(cqmin(2)+cqplus(2))/i
        cqnet(3)=(cqmin(3)+cqplus(3))/i
	  cqnetA(1)=(cqnet(1)-goff)/scale+oldmid(1)
	  cqnetA(2)=(cqnet(2)-goff)/scale+oldmid(2)
	  cqnetA(3)=(cqnet(3)-goff)/scale+oldmid(3)
c     calcolo  raggio medio molecola
        tmp=0.
        do i=1,ibnum
          tmp=tmp+(scspos(1,i)-cqnetA(1))**2+(scspos(2,i)-cqnetA(2))**2
          tmp=tmp+(scspos(3,i)-cqnetA(3))**2
        end do
        radius=sqrt(tmp/ibnum)+exrad

        ergestemp=0.0
        do 9134 iz=1,igrid
          cutedgesz=-2.5
          if (iz.eq.1.or.iz.eq.igrid) cutedgesz=2.
          do 9135 iy=1,igrid
            cutedges=cutedgesz
            if (iy.eq.1.or.iy.eq.igrid) cutedges=cutedgesz+1
            do 9137 ic = 1,nqass
              dist1=1-atmcrg(1,ic)
              dist =dist1**2+(atmcrg(2,ic)-iy)**2+(atmcrg(3,ic)-iz)**2
              dist = sqrt(dist)/scale
              tempd=atmcrg(4,ic)*exp(-dist/deblen)/(dist*epsout)
              phimap(1,iy,iz) = phimap(1,iy,iz) + tempd
            
              dist1=igrid-atmcrg(1,ic)
              dist =dist1**2+(atmcrg(2,ic)-iy)**2+(atmcrg(3,ic)-iz)**2
              dist = sqrt(dist)/scale
              tempd=atmcrg(4,ic)*exp(-dist/deblen)/(dist*epsout)
              phimap(igrid,iy,iz) = phimap(igrid,iy,iz) + tempd
9137        continue
            dist1=1-cqnet(1)
            dist =dist1**2+(cqnet(2)-iy)**2+(cqnet(3)-iz)**2
	      dist = sqrt(dist)/scale
            fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
	      dist1=dist1*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
	      ergestemp=ergestemp+qnet*tempd*dist1/dist**2
            dist1=igrid-cqnet(1)
            dist =dist1**2+(cqnet(2)-iy)**2+(cqnet(3)-iz)**2
	      dist = sqrt(dist)/scale
	      fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
            dist1=dist1*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
            ergestemp=ergestemp-qnet*tempd*dist1/dist**2
9135      continue
9134    continue       
        if (.not.iper(1)) ergestout=ergestout+ergestemp
        ergestemp=0.0
        do 9138 iz=1,igrid
          cutedgesz=-2.5
          if (iz.eq.1.or.iz.eq.igrid) cutedgesz=2.
          do 9140 ix=1,igrid
            cutedges=cutedgesz
            if (ix.eq.1.or.ix.eq.igrid) cutedges=cutedgesz+1
            do 9141 ic = 1,nqass
              dist2=1-atmcrg(2,ic) 
              dist=(atmcrg(1,ic)-ix)**2+dist2**2+(atmcrg(3,ic)-iz)**2
              dist = sqrt(dist)/scale
              tempd=atmcrg(4,ic)*exp(-dist/deblen)/(dist*epsout)
              phimap(ix,1,iz) = phimap(ix,1,iz) + tempd

              dist2=igrid-atmcrg(2,ic)
              dist=(atmcrg(1,ic)-ix)**2+dist2**2+(atmcrg(3,ic)-iz)**2
              dist = sqrt(dist)/scale
              tempd=atmcrg(4,ic)*exp(-dist/deblen)/(dist*epsout)
              phimap(ix,igrid,iz) = phimap(ix,igrid,iz) + tempd
9141        continue
            dist2=1-cqnet(2)
            dist =dist2**2+(cqnet(1)-ix)**2+(cqnet(3)-iz)**2
	      dist = sqrt(dist)/scale
            fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
	      dist2=dist2*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
	      ergestemp=ergestemp+qnet*tempd*dist2/dist**2
            dist2=igrid-cqnet(2)
            dist =dist2**2+(cqnet(1)-ix)**2+(cqnet(3)-iz)**2
	      dist = sqrt(dist)/scale
	      fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
            dist2=dist2*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
            ergestemp=ergestemp-qnet*tempd*dist2/dist**2
9140      continue
9138    continue    
        if (.not.iper(2)) ergestout=ergestout+ergestemp
        ergestemp=0.0
        do 9143 iy=1,igrid
          cutedgesy=-2.5
          if (iy.eq.1.or.iy.eq.igrid) cutedgesy=2.
          do 9144 ix=1,igrid
            cutedges=cutedgesy
            if (ix.eq.1.or.ix.eq.igrid) cutedges=cutedgesy+1
            do 9145 ic = 1,nqass
              dist3=1-atmcrg(3,ic)
              dist=(atmcrg(1,ic)-ix)**2+(atmcrg(2,ic)-iy)**2+dist3**2
              dist = sqrt(dist)/scale
              tempd=atmcrg(4,ic)*exp(-dist/deblen)/(dist*epsout)
              phimap(ix,iy,1) = phimap(ix,iy,1) + tempd

              dist3=igrid-atmcrg(3,ic)
              dist=(atmcrg(1,ic)-ix)**2+(atmcrg(2,ic)-iy)**2+dist3**2
              dist = sqrt(dist)/scale
              tempd=atmcrg(4,ic)*exp(-dist/deblen)/(dist*epsout)
              phimap(ix,iy,igrid) = phimap(ix,iy,igrid) + tempd       
9145        continue
            dist3=1-cqnet(3)
            dist =dist3**2+(cqnet(2)-iy)**2+(cqnet(1)-ix)**2
	      dist = sqrt(dist)/scale
            fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
	      dist3=dist3*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
	      ergestemp=ergestemp+qnet*tempd*dist3/dist**2
            dist3=igrid-cqnet(3)
            dist =dist3**2+(cqnet(2)-iy)**2+(cqnet(1)-ix)**2
	      dist = sqrt(dist)/scale
	      fact=exp(-(dist-radius)/deblen)/(1+radius/deblen)
            dist3=dist3*(3.5-cutedges)/6.
            tempd=qnet*fact/(dist*epsout)
            ergestemp=ergestemp-qnet*tempd*dist3/dist**2
9144      continue
9143    continue
        if (.not.iper(3)) ergestout=ergestout+ergestemp
        ergestout=ergestout*rionst*deblen*.0006023/(epsout*scale**3)
      end if 
c
c end of the option for the complete summation of potential
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++


c---------------------------------------------------------------
	midg = (igrid+1)/2
	write(6,*)' some initial phi values: '
	write(6,*)' midg,midg,1; midg,midg,igrid '
	write(6,*)phimap(midg,midg,1), phimap(midg,midg,igrid)
	write(6,*)' midg,1,midg; midg,igrid,midg '
	write(6,*)phimap(midg,1,midg),phimap(midg,igrid,midg)
	write(6,*)' 1,midg,midg; igrid,midg,midg '
	write(6,*)phimap(1,midg,midg),phimap(igrid,midg,midg)
C---------------------------------------------------------------
	return
900	write(6,*)' no potl map for focussing boundary conditions'
   	stop
	end
