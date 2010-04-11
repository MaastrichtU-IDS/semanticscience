	subroutine react(nqass,icount1b,ibnum,ergs,ergas,natom,nmedia)
	include 'qdiffpar4.h'
	include 'qlog.h'
c
	real phimap(igrid,igrid,igrid)
	logical ido
	dimension sqs(1),ibgrd(3,ibnum),cqs(ncrgmx)
	dimension mv(6)
	dimension cgrid(1),xo(3),xn(3),sen(1)
	dimension spdiv(1),gchrg(icount1b)
	dimension spot(1),scspos(3,ibnum)
	integer gchrgp(3,icount1b)
c gchrgp= (i,j,k)  for the icount1b charged grid points
	character*80 line
c b+++++++++++++++++++++
        real rad3(natom),atmeps(nqass),radius,ergsrea,cost
        real cgbp(5,ibc),atmcrg(4,nqass),chgpos(3,nqass)
        integer crgatn(1),jj,qq
        character*15 atinf(natom)
        real medeps(0:nmedia),dista
c e++++++++++++++++++++
c
	i_schrg= memalloc(i_schrg,4*ibnum)
	i_sqs= memalloc(i_sqs,4*ibnum)
	i_spdiv= memalloc(i_spdiv,4*ibnum)
	i_sen= memalloc(i_sen,4*ibnum)
	i_spot= memalloc(i_spot,4*ibnum)
        i_cqs= memalloc(i_cqs,4*nqass)
c fact=six divide by 4 pi, multiplied by epkt, scale
c
c b+++++++++deleted epsval in order to have usual srf charge definition
	fact=0.9549296586/(2.0*scale*epkt)
c e+++++++++++++++++++++++
	sixth=1.0/6.0
	en1=0.0
        ergsrea=0.0
c       write(6,*)scspos(1,1),scspos(2,1),scspos(3,1)
c
c calculate surface charge
c
c b+++++++++++++++++++++++++++++++++++++++++++
c       goff = (igrid + 1.)/2.
c       eps2=1.
c       eps1=80
c       co=1.*561/eps2
c       d=3
c       epsdim=5

c       write(6,*)'faccio..',co
c       ix=goff
c       iy=goff
c       xx=(ix-goff)/scale +oldmid(1)
c       yy=(iy-goff)/scale +oldmid(2)

c       do 9000 iz=1,igrid
c         zz=(iz-goff)/scale +oldmid(3)
c         dista=sqrt(xx**2+yy**2+(zz+d)**2)
c         if (zz.lt.0) then
c           phi=1./dista
c           phi=phi+(eps2-eps1)/((eps1+eps2)*sqrt(xx**2+yy**2+
c    &(zz-d)**2))
c         else
c           phi=2.*eps2/((eps1+eps2)*dista)
c         end if
c         write(6,*)'point:',iz,zz
c         write(6,*)'calculated=',phimap(ix,iy,iz)
c         write(6,*)'analytical:',co*phi
c         write(6,*)''
c9000    continue
c e++++++++++++++++++++++++++++++++++++++++++++++
          
        do i=1,ibnum
          ix=ibgrd(1,i)
          iy=ibgrd(2,i)
          iz=ibgrd(3,i)
          temp1=phimap(ix+1,iy,iz)+phimap(ix-1,iy,iz)
          temp2=phimap(ix,iy+1,iz)+phimap(ix,iy-1,iz)
          temp3=phimap(ix,iy,iz+1)+phimap(ix,iy,iz-1)
          spdiv(i)=phimap(ix,iy,iz)-(temp1+temp2+temp3)*sixth
c         if(scspos(3,i).eq.0.) then
c           ttemp=(scspos(1,i)**2+scspos(2,i)**2+(scspos(3,i)+3)**2)
c           ttemp=sqrt(ttemp)
c           write(6,*)'pot',phimap(ix,iy,iz),'vero=',561/(42*ttemp)
c         end if
        end do

	if(ibc.ne.0)then
	  i_cgrid= memalloc(i_cgrid,4*igrid**3)
          call rdiv(igrid,ibnum,ibc,ibgrd,spdiv,cgbp,cgrid,ergsrea)
	  i_cgrid= memalloc(i_cgrid,0)
	endif
c
c spdiv is equal to the 'charge' as would appear on the grid
c to replace the boundary elements
c
	en1=0.0
	do i=1,ibnum
	  schrg(i)=spdiv(i)*fact
	  en1=en1+(schrg(i))
	end do
c
c attempt to spread charge about a bit..
c	ispread=.true.
	nscrg=ibnum
c	write(6,*) "changed ",ibnum," charges to ",nscrg

c
c generate pseudo distances for surface points
c
	if(irea.or.logs.or.lognl.or.isen.or.isch) then
        do i=1,ibnum
          sqs(i)=(scspos(1,i)**2+scspos(2,i)**2+scspos(3,i)**2)/2.0
        end do
c
	if(logs.or.lognl) then
c
c calculate back energies
c
          en=0.0
          en2=0.0
          en3=0.0
          ent=0.0
c
c b+++++++++++++++++++++++++++++++++++++++++
c calculating interaction energy between each real charge and 
c the surrounding polarization charges

          if (nmedia.gt.0) then          
            do i=1,nqass
              radius=radpolext
              ii=crgatn(i)
              if(ii.gt.0.and.ii.le.natom) radius=rad3(ii)
c cost=1/eps-1
              cost=(1./(epkt*atmeps(i))-1.) 
              if (atmeps(i).le.0.) write(6,*)'atmeps error',i,ii
              if (radius.le.0.) then
                 write(6,*)'charged atom number',ii,
     &'radius changed from zero to ',radpolext
                 write(6,*)'BE CAREFUL!! REACTION FIELD ENERGY MIGHT BE
     & OVERESTIMATED!!!!'
                 radius=radpolext
              end if
              ergsrea=ergsrea+0.5*atmcrg(4,i)*atmcrg(4,i)*cost/radius
            end do
            ergsrea=ergsrea*epkt
            write(6,*) 'self-reaction field energy :    '
     &,ergsrea,' kt'
            if(inrgwrt) write(42,'(a30,f10.4,a4)') 'self-reaction
     &  field energy:',ergsrea,' kt'
          end if
c e++++++++++++++++++++++++++++++

	  if(ibufz) then
 	    do i=1,nqass
	     dist1=chgpos(1,i)
	     dist2=chgpos(2,i)
	     dist3=chgpos(3,i)
	     cqs(i)=(dist1**2 + dist2**2 + dist3**2)/2.0
	    end do
	    en=0.0
	    limx1=2+bufz(1,1)
	    limx2=igrid-1-bufz(2,1)
	    limy1=2+bufz(1,2)
	    limy2=igrid-1-bufz(2,2)
	    limz1=2+bufz(1,3)
	    limz2=igrid-1-bufz(2,3)
	    do 51 j=1,ibnum
             ix=ibgrd(1,j)
             iy=ibgrd(2,j)
             iz=ibgrd(3,j)
             ido=.true.
             if((ix.lt.limx1).or.(ix.gt.limx2)) ido=.false.
             if((iy.lt.limy1).or.(iy.gt.limy2)) ido=.false.
     	     if((iz.lt.limz1).or.(iz.gt.limz2)) ido=.false.
     	     if(ido) then
     	      dist1=scspos(1,j)
     	      dist2=scspos(2,j)
     	      dist3=scspos(3,j)
     	      dist4=sqs(j)
     	      schrgj=schrg(j)/sqrt(2.0)
     	      en1=0.0
     	      ent=ent+schrg(j)
     	      do 41 i=1,nqass
               prod=dist1*chgpos(1,i)+dist2*chgpos(2,i)+dist3*
     &  chgpos(3,i)
	       dist=dist4+cqs(i)-prod
	       temp=atmcrg(4,i)/sqrt(dist)
	       en1=en1+temp
41	      continue
	      en=en+en1*schrgj
	      sen(j)=schrgj*en1
	     end if
51	    continue
c b+++++++++deleted epsval
	    ergs=en*epkt/2.0
            write(6,'(f10.4)')'tot s.charge, no epsin carrying :',ent
            write(6,*) 'corrected reaction field energy:      ',ergs,
     &' kt'
            write(6,*)'total reaction field energy    :  ',ergsrea+ergs,
     &'kt'
	    if(inrgwrt) then
              write(42,'(a30,f10.4,a4)') 'corrected reaction field 
     &  energy:',ergs,' kt'
              write(42,'(a30,f10.4,a4)') 'total reaction field energy:'
     &  ,ergs+ergsrea,' kt'
            end if
c e+++++++++++++++++++++++++
	  end if
 
	  if(.not.ibufz) then
	   avp=0.0
c       open(52,file='scsposnew',form='formatted')

	   do i=1,nscrg
	    sdist1=scspos(1,i)
	    sdist2=scspos(2,i)
	    sdist3=scspos(3,i)
c          write (52,'(I4,3f8.3)') i,scspos(1,i),scspos(2,i),scspos(3,i)

            ptemp=0.0
	    do j=1,nqass
             dist1=chgpos(1,j)
             dist2=chgpos(2,j)
             dist3=chgpos(3,j)
	     dist=sqrt((sdist1-dist1)**2+(sdist2-dist2)**2+(sdist3-
     &  dist3)**2)
	     ptemp=ptemp+atmcrg(4,j)/dist
	    end do
	    spot(i)=ptemp
	    avp=avp+ptemp
	   end do
c           close(52) 
 
	   en=0.0
	   ent=0.0
	   do i=1,nscrg
	    temp=spot(i)*schrg(i)
	    ent=ent+schrg(i)
	    en=en+temp
	   end do
 
c b+++++++++deleted epsval
   	   ergs=en*epkt/2.0

	 write(6,'(a35,f10.4)')"total s.charge,no epsin carrying :",ent
         write(6,*)'corrected reaction field energy: ',ergs,' kt'
	 write(6,*)'total reaction field energy :   ',ergsrea+ergs,' kt'
          if(inrgwrt) then
             write(42,'(a35,f10.4,a4)') 'corrected reaction field
     &  energy:',ergs,' kt'
             write(42,'(a30,f10.4,a4)') 'total reaction field energy:'
     &  ,ergs+ergsrea,' kt'
            end if
c e++++++++++++++++++++++++
	  end if
c
c end of solvation calculation..
	end if
c
	if(isch) then
	write(6,'(2a28)') "writing surface charge file:",scrgnam(:scrgle
     &  n)
	if((scrgfrm.eq.0).or.(scrgfrm.eq.1)) open(41,file=scrgnam(:scrgl
     &  en))
c	if(scrgfrm.eq.2) open(41,file=scrgnam(:scrglen),access="append")
	 if(scrgfrm.eq.2) open(41,file=scrgnam(:scrglen))
	 write(41,'(a17)') "DELPHI FORMAT PDB"
	 write(41,'(a15)') "FORMAT NUMBER=2"
c adjusted for spread charges
	 if(ibufz) then
          limx1=2+bufz(1,1)
          limx2=igrid-1-bufz(2,1)
          limy1=2+bufz(1,2)
          limy2=igrid-1-bufz(2,2)
          limz1=2+bufz(1,3)
          limz2=igrid-1-bufz(2,3)
	 end if
	 do i=1,nscrg
          ix=ibgrd(1,i)
          iy=ibgrd(2,i)
          iz=ibgrd(3,i)
c
	  if(ibufz) then
           ido=.true.
           if((ix.lt.limx1).or.(ix.gt.limx2)) ido=.false.
           if((iy.lt.limy1).or.(iy.gt.limy2)) ido=.false.
           if((iz.lt.limz1).or.(iz.gt.limz2)) ido=.false.
	   if(.not.ido) then
	    goto 450
	   end if
	  end if
c
	  xo(1)=scspos(1,i)
	  xo(2)=scspos(2,i)
	  xo(3)=scspos(3,i)
	  en1=schrg(i)
c b+++++++++deleted epsval
	  spt1=spot(i)*en1*epkt/2.0
c e+++++++++++++++++++++++

	  if(scrgfrm.eq.0)write(41,414) i,xo,en1
c
	  if((scrgfrm.eq.1).or.(scrgfrm.eq.2)) then
          jj=atsurf(i)
          read(atinf(jj)(12:15),'(I4)')qq
c      qq= residue sequence number
	    call watpte(i,qq,xo,line,en1,spt1)
	    write(line(12:16),'(I5)')jj
	    write(41,80) line
	  end if
c
450	  continue
	 end do
	 close(41)
	end if
80	format(a80)
c
	if(isen) then
c
c sen will now not be correct since schrg was changed
c
	 write(6,'(a40)') "writing surface energy file: surfen.dat"
	 open(41,file="surfen.dat")
	 en2=0.0
	 do i=1,ibnum
	  xo(1)=scspos(1,i)
	  xo(2)=scspos(2,i)
	  xo(3)=scspos(3,i)
c	call gtoc(xo,xn)
	  en1=sen(i)/2.0
	  write(41,414) i,xo,en1
	 end do
	 close(41)
	end if
c
	end if
c if isen, calculate surface energy positions and values
c
414	format(i5,3f8.3,f8.3)
c
	i_sqs= memalloc(i_sqs,0)
	i_spdiv= memalloc(i_spdiv,0)
	i_sen= memalloc(i_sen,0)
	i_spot= memalloc(i_spot,0)
        i_cqs= memalloc(i_cqs,0)

	return
	end
