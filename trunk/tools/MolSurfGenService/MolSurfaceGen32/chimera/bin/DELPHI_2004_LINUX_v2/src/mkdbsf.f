	subroutine mkdbsf(ibnum,nsp,dbval,icount2a,icount2b,sfd,natom,
     &  nmedia,idirectalg,nobject)
c
	include "qdiffpar4.h"
	include "qlog.h"
c
        integer iepsmp(igrid,igrid,igrid,3)
        logical*1 idebmap(igrid,igrid,igrid)
c b+++++++++++++++++++++++
        real medeps(0:nmedia)
        real denom,vecttemp(6)
        integer idirectalg,epsdim,nobject
c e+++++++++++++++++++++++
        real phimap3(ngp)

	dimension sf1(nhgp),sf2(nhgp),dbval(0:1,0:6,0:1)
	dimension ibgrd(3,ibnum),db(6,nsp),idpos(nsp)
	dimension iepsv(nsp),sfd(5,0:1)
	integer deb,it(6)
c
	i_iepsv= memalloc(i_iepsv,4*nsp)
	i_phimap3= memalloc(i_phimap3,4*ngp)

c
 	debfct = epsout/(deblen*scale)**2
        sixeps=epsout*6.0
	sixth=1.0/6.0
	sixsalt=sixth*((1/(1+debfct/sixeps))-1.0)
	isgrid=igrid**2
c initialisation of idpos+++++++++++++++
c       do ix=1,nsp
c          idpos(ix)=0 no longer needed, calloc superseded malloc
c       end do
        epsdim=natom+nobject+2
c +++++++++++++++++++++++++++++++++++++
c
	ibnum1=0
	ibnum2=nsp/2
	idbs=0
	dbs=0.
c
	if(idbwrt) then
	open(13,file=dbnam(:dblen))
	write(13,*) "DELPHI DB FILE"
	write(13,*) "FORMAT NUMBER=1"
	write(13,*) "NUMBER OF BOUNDARY POINTS= ",ibnum
	end if
c
	do 774 ix=1,ibnum
	  i=ibgrd(1,ix)
	  j=ibgrd(2,ix)
	  k=ibgrd(3,ix)
c
        if (idirectalg.eq.0) then
	  it(1)=0
	  it(2)=0
	  it(3)=0
	  it(4)=0
	  it(5)=0
	  it(6)=0
	  ieps=0
c b+++++++++++++++++
	  if((iepsmp(i,j,k,1)/epsdim).ne.0) it(1)=1
	  if((iepsmp(i,j,k,2)/epsdim).ne.0) it(2)=1
	  if((iepsmp(i,j,k,3)/epsdim).ne.0) it(3)=1
	  if((iepsmp(i-1,j,k,1)/epsdim).ne.0) it(4)=1
	  if((iepsmp(i,j-1,k,2)/epsdim).ne.0) it(5)=1
	  if((iepsmp(i,j,k-1,3)/epsdim).ne.0) it(6)=1
	  ieps=it(1)+it(2)+it(3)+it(4)+it(5)+it(6)
        else
          ieps=0
          temp=0
          itmp=iepsmp(i,j,k,1)/epsdim
          temp=temp+medeps(itmp)
          vecttemp(1)=medeps(itmp)
          itmp=iepsmp(i,j,k,2)/epsdim
          temp=temp+medeps(itmp)
          vecttemp(2)=medeps(itmp)
          itmp=iepsmp(i,j,k,3)/epsdim
          temp=temp+medeps(itmp)
          vecttemp(3)=medeps(itmp)
          itmp=iepsmp(i-1,j,k,1)/epsdim
          temp=temp+medeps(itmp)
          vecttemp(4)=medeps(itmp)
          itmp=iepsmp(i,j-1,k,2)/epsdim
          temp=temp+medeps(itmp)
          vecttemp(5)=medeps(itmp)
          itmp=iepsmp(i,j,k-1,3)/epsdim
          temp=temp+medeps(itmp)
          vecttemp(6)=medeps(itmp)
c e+++++++++++++++++
        end if
          deb=0
          if (idebmap(i,j,k)) deb=1
	  if(deb.eq.1) then
	  idbs=idbs+1
	  end if
c
	  iw=isgrid*(k-1) + igrid*(j-1) + i
	  iv=(iw+1)/2
	  if(iw.ne.(2*iv)) then
		ibnum1=ibnum1+1
		ibnum3=ibnum1
	  else
		ibnum2=ibnum2+1
		ibnum3=ibnum2
	  end if
c
	  idpos(ibnum3) = iv
	  iepsv(ibnum3) = ieps

        if (idirectalg.eq.0) then
	  db(1,ibnum3)=dbval(it(4),ieps,deb)
	  db(2,ibnum3)=dbval(it(1),ieps,deb)
	  db(3,ibnum3)=dbval(it(5),ieps,deb)
	  db(4,ibnum3)=dbval(it(2),ieps,deb)
	  db(5,ibnum3)=dbval(it(6),ieps,deb)
	  db(6,ibnum3)=dbval(it(3),ieps,deb)
        else
c b+++++++++++++++
          denom=temp+deb*debfct
          if (rionst.eq.0.) then
            db(1,ibnum3)=vecttemp(4)/denom -sixth
            db(2,ibnum3)=vecttemp(1)/denom -sixth
            db(3,ibnum3)=vecttemp(5)/denom -sixth
            db(4,ibnum3)=vecttemp(2)/denom -sixth
            db(5,ibnum3)=vecttemp(6)/denom -sixth
            db(6,ibnum3)=vecttemp(3)/denom -sixth
          else
            db(1,ibnum3)=vecttemp(4)/denom
            db(2,ibnum3)=vecttemp(1)/denom
            db(3,ibnum3)=vecttemp(5)/denom
            db(4,ibnum3)=vecttemp(2)/denom
            db(5,ibnum3)=vecttemp(6)/denom
            db(6,ibnum3)=vecttemp(3)/denom
          end if
c e+++++++++++++++          
        end if
	if(idbwrt) write(13,400) i,j,k,(db(l,ibnum3),l=1,6)
400	format(i2,x,i2,x,i2,6f12.8)
	  dbs=dbs+db(1,ibnum3)
774	continue
c +++++debug+++++++
c       if (debug) write(6,*)'WWW ibnum3=',ibnum3
c ++++++++++++++++++++
c
	if(idbwrt) close(13)
	write(6,*) "no. dielectric boundary points in salt = ",idbs
c
c realign idpos and db,compressing to contingous space
c
	icount2a=ibnum1
	icount2b=icount2a+ibnum2-(nsp/2)

	itemp=(nsp/2)
	do 781 ix=icount2a+1,icount2b
	itemp=itemp+1
	idpos(ix)=idpos(itemp)
	iepsv(ix)=iepsv(itemp)
	db(1,ix)=db(1,itemp)
	db(2,ix)=db(2,itemp)
	db(3,ix)=db(3,itemp)
	db(4,ix)=db(4,itemp)
	db(5,ix)=db(5,itemp)
	db(6,ix)=db(6,itemp)
781	continue
c
c set saltmaps 1 and 2
c NB phimap3 used as a dummy flat 65**3 array
c
	if(rionst.gt.0.) then
	iw=1
	do 841 iz=1,igrid
	  do 842 iy=1,igrid
	    do 843 ix=1,igrid
              deb=0
              if (idebmap(ix,iy,iz)) deb=1
              phimap3(iw)=sixth + deb*sixsalt
	      iw=iw+1
843	continue
842	continue
841	continue
c
	iy=0
	icgrid=igrid*igrid*igrid
	sf1((icgrid+1)/2)=phimap3(icgrid)
c
	do 850 ix=1,icgrid-2,2
	iy=iy+1
	sf1(iy)=phimap3(ix)
	sf2(iy)=phimap3(ix+1)
850	continue
c
        do 844 ix=1,icount2a
c b+++++++++++++++
        if (idirectalg.ne.0) then
           sf1(idpos(ix))= 0.0
        else
c e+++++++++++++++
           i=1
           if(sf1(idpos(ix)).eq.sixth) i=0
           sf1(idpos(ix))=sfd(iepsv(ix),i)
        end if 
844     continue
c
        do 845 ix=icount2a+1,icount2b
c b+++++++++++++++
        if (idirectalg.ne.0) then
            sf2(idpos(ix))= 0.0
        else
c e+++++++++++++++
           i=1
           if(sf2(idpos(ix)).eq.sixth) i=0
           sf2(idpos(ix))=sfd(iepsv(ix),i)
        end if
845     continue
c
	end if
c
	i_iepsv= memalloc(i_iepsv,0)
	i_phimap3= memalloc(i_phimap3,0)
c
	return
	end
