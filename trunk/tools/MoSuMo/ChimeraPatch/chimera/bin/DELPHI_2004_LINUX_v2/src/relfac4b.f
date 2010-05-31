	subroutine relfac(idpos,db,sf1,sf2,icount2a,icount2b,spec,ibnum,
     &	phimap1,phimap2,phimap3,bndx,bndy,bndz,idirectalg)
c
	include 'qdiffpar5.h'
	include 'qlog.h'
c 
	dimension bndx(nbgp),bndy(nbgp),bndz(nbgp)
	dimension sn1(ngrid),sn2(ngrid),sn3(ngrid)
	dimension db(6,ibnum),sf1(nhgp),sf2(nhgp)
	integer idpos(ibnum),idirectalg
	integer star,fin,sta1(ngrid),sta2(ngrid),fi1(ngrid),fi2(ngrid)
        real phimap1(nhgp),phimap2(nhgp),phimap3(ngp),recipr
c
	sixth = 1./6.
	icgrid=igrid**3
	ihgd=(igrid+1)/2
c b++++++++++++debug++++++++++++++++++++++++
c       open(52,FILE='idpos')
c            write(52,*)'ibnum=',icount2b
c            do iz=1,ibnum
c              write(52,*)idpos(iz)
c            end do
c       close (52)
c       open(52,FILE='db')
c       do ix=1,ibnum
c         s=1./6.
c         write(52,*)db(1,ix)-s,db(2,ix)-s,db(3,ix)-s,db(4,ix)-s,
c    &  db(5,ix)-s,db(6,ix)-s     
c       end do
c       close (52)
c       open(52,FILE='sf1')
c            do iz=1,nhgp 
c              write(52,*)sf1(iz)
c            end do
c       close (52)
c       open(52,FILE='sf2')
c            do iz=1,nhgp 
c              write(52,*)sf2(iz)
c            end do
c       close (52)
c e++++++++++++++++++++++++++++++++++++++++++
c       do ix=1,nhgp
c          phimap1(ix)=0.0
c          phimap2(ix)=0.0
c       end do
c       do ix=1,ngp
c          phimap3(ix)=0.0
c       end do
c       if(iper(1)) then
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
c set up sn array for lowest eigenstate
c
      i=0
	sn1(1)=0.0
	sn1(igrid)=0.0
	sn2(1)=0.0
	sn2(igrid)=0.0
	sn3(1)=0.0
	sn3(igrid)=0.0
	do 550 ix=2,igrid-1
          temp=3.14159265*float(ix-1)/float(igrid-1)
          sn1(ix)=sqrt(2.0)*sin(temp)/sqrt(float(igrid-1))
	  sn2(ix)=sn1(ix)
	  sn3(ix)=sn1(ix)
550	continue
        recipr=1.0/sqrt(float(igrid))
	if(iper(1)) then
	  do 571 ix=1,igrid
571         sn1(ix)=recipr
	end if
	if(iper(2)) then
	  do 572 iy=1,igrid
572	    sn2(iy)=recipr
	end if
	if(iper(3)) then
	  do 573 iz=1,igrid
573	    sn3(iz)=recipr
	end if
c
	iw=1
	do 301 iz=1,igrid
	  temp3=sn3(iz)
	  do 302 iy=1,igrid
	    temp2=temp3*sn2(iy)
	    do 303 ix=1,igrid
	      phimap3(iw)=temp2*sn1(ix)
	      iw=iw+1
303         continue
302       continue
301     continue
	temp=0.0
	do 500 ix=2,icgrid-1,2
	iy=ix/2
	phimap2(iy)=phimap3(ix)
	temp=temp + phimap3(ix)**2
500	continue 
c
	if(rionst.gt.0.0) then
        do 9004 n = 2, igrid-1
	  star=sta1(n)
	  fin=fi1(n)
          do 9006 ix = star,fin
            temp1 = phimap2(ix) + phimap2(ix-1)
            temp2 = phimap2(ix+lat1) + phimap2(ix-lat2)
            temp3 = phimap2(ix+long1) + phimap2(ix-long2)
       	    phimap1(ix) = (temp1+temp2+temp3)*sf1(ix)
9006	  continue
9004	continue
c
c otherwise the main loop is as below:
c
        else
c
        do 9104 n = 2, igrid-1
	  star=sta1(n)
	  fin=fi1(n)
          do 9106 ix = star,fin
            temp1 = phimap2(ix) + phimap2(ix-1)
            temp2 = phimap2(ix+lat1) + phimap2(ix-lat2)
            temp3 = phimap2(ix+long1) + phimap2(ix-long2)
       	    phimap1(ix) =  (temp1+temp2+temp3)*sixth
9106	  continue
9104	continue
        end if
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
              phimap1(ix)=(temp1+.5*(temp2+temp3+rtemp2+rtemp3))*(
     &                    sf1(ix)+sf1(ix+lat1))*.5
c now updating last slice
              phimap1(ix+lat1)=phimap1(ix)
              ix=ix+igrid
            end do
          else
            do n=1,(igrid-3)*lat2+1
              temp1 = phimap2(ix)+phimap2(ix-1+lat1)
              temp2 = phimap2(ix+lat1) + phimap2(ix-lat2)
              temp3 = phimap2(ix+long1) + phimap2(ix-long2)
              phimap1(ix)=(temp1+temp2+temp3)*sixth
c now updating last slice
              phimap1(ix+lat1)=phimap1(ix)
              ix=ix+igrid
            end do
          end if
        end if
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

c
C$DIR NO_RECURRENCE 
	do 9010 k=1,icount2a
	  ix=idpos(k)
	  temp1=phimap2(ix-1)*db(1,k)+phimap2(ix)*db(2,k)
	  temp2=phimap2(ix-lat2)*db(3,k)+phimap2(ix+lat1)*db(4,k)
	  temp3=phimap2(ix-long2)*db(5,k)+phimap2(ix+long1)*db(6,k)
	  phimap1(ix)= phimap1(ix) + temp1+temp2+temp3
9010    continue
c       end if
c
c Now reset boundary values altered in above loops.
c 
	star=igrid*(igrid+1)/2
	fin=igrid*(igrid*(igrid-1)-2)/2
C$DIR NO_RECURRENCE
	do 9201 ix=star,fin,igrid
	  phimap1(ix+1)=0.0
	  phimap1(ix+ihgd)=0.0
9201    continue
c b++++++++++++debug++++++++++++++++++++++++
c       open(52,FILE='phimap1')
c            do ix=1,137313
c              write(52,*)phimap1(ix)
c            end do
c       close (52)
c e++++++++++++++++++++++++++++++++++++++++++
c
	temp=0.0
	do 1500 ix=1,(icgrid-1)/2
	temp=temp + phimap1(ix)*phimap3(2*ix-1)
1500	continue 
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
c Next update phimap3 using the new phimap1
c
        if(rionst.gt.0.0) then	
        do 8004 n = 2, igrid-1
	  star=sta2(n)
	  fin=fi2(n)
          do 8006 ix = star,fin
            temp1 = phimap1(ix) + phimap1(ix+1)
            temp2 = phimap1(ix+lat2) + phimap1(ix-lat1)
            temp3 = phimap1(ix+long2) + phimap1(ix-long1)
       	    phimap3(ix) =(temp1+temp2+temp3)*sf2(ix)
8006	  continue
8004	continue
c
	else
c
        do 8104 n = 2, igrid-1
	  star=sta2(n)
	  fin=fi2(n)
          do 8106 ix = star,fin
            temp1 = phimap1(ix) + phimap1(ix+1)
            temp2 = phimap1(ix+lat2) + phimap1(ix-lat1)
            temp3 = phimap1(ix+long2) + phimap1(ix-long1)
       	    phimap3(ix) = (temp1+temp2+temp3)*sixth
8106	  continue
8104	continue
	end if
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
              phimap3(ix)=(temp1+.5*(temp2+temp3+rtemp2+rtemp3))*(
     &                    sf2(ix)+sf2(ix+lat1))*.5
c now updating last slice
              phimap3(ix+lat1)=phimap3(ix)
            end do
          else
            do n=1,long1-igrid-1
              ix=ix+igrid
              temp1 = phimap1(ix+lat1)  + phimap1(ix+1)
              temp2 = phimap1(ix+lat2)  + phimap1(ix-lat1)
              temp3 = phimap1(ix+long2) + phimap1(ix-long1)
              phimap3(ix)=(temp1+temp2+temp3)*sixth
c now updating last slice
              phimap3(ix+lat1)=phimap3(ix)
            end do
          end if
        end if
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

c
C$DIR NO_RECURRENCE 
	do 8010 k=icount2a+1,icount2b
	ix=idpos(k)
	temp1=phimap1(ix)*db(1,k)+phimap1(ix+1)*db(2,k)
	temp2=phimap1(ix-lat1)*db(3,k)+phimap1(ix+lat2)*db(4,k)
	temp3=phimap1(ix-long1)*db(5,k)+phimap1(ix+long2)*db(6,k)
	phimap3(ix)=phimap3(ix) + temp1+temp2+temp3
8010    continue
c reset boundary condition
c
	star=(igrid+2)/2
	iy=(igrid*(igrid+2)/2) - igrid +1
	fin=(igrid*(igrid-1)-1)/2
	ihgd2=ihgd-1
C$DIR NO_RECURRENCE
	do 8201 ix=star,fin
	iy=iy+igrid
	phimap3(iy)=0.0
	phimap3(iy+ihgd2)=0.0
8201    continue
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
	    phimap3(itemp1)=phimap1(itemp2)
	    phimap3(itemp3)=phimap1(itemp4)
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
            phimap3(itemp1)=phimap1(itemp2)
            phimap3(itemp3)=phimap1(itemp4)
8015	  continue
        end if
c
	temp=0.0
	do 2000 ix=1,(icgrid-1)/2
	temp=temp + (phimap3(ix)*phimap2(ix))
2000	continue 
	spec=(2.0*temp)
c following needed as spec exceeds 1.0 occasionally in focussing calculations
c (SS May 8, 1998)
        if(spec.gt.1.0)spec=0.995
	write(6,*) ' '
	write(6,'(A31,F20.10)')'gauss-seidel spectral radius is',spec
	write(6,*) ' '
c
	return
	end
