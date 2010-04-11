	subroutine setout(natom,radprobe,exrad,scale,igrid,nobject
     &  ,oldmid)
	include 'pointer.h'
c
	dimension xn2(3,natom),rad3(natom),xn(3)
	integer ioff(3,1),ismin(3),ismax(3)
	dimension sq1(-15:15),sq2(-15:15),sq3(-15:15)
	dimension rad2a1(-15:15),rad2a2(-15:15),rad2a3(-15:15)
	dimension iepsmp(igrid,igrid,igrid,3)
c b+++++++++++
        integer nobject,imedia,objecttype,epsdim,kind
        character*80 dataobject(nobject,2)
        character*80 strtmp,strtmp1
        dimension iatmmed(natom+nobject)
        real limgunit(3,2,nobject),vectz(3)
        real radprobe,exrd,modul2,axdist
c here radprb is not zero only if one wants to map the extended surf.
c that has to be done with radprb(1) if solute-solvent interface is
c concerned
        real rmid,oldmid(3),tmpvect(3),tmp,tmp1,dx,dy,dz,dist,zeta
        real xa(3),xb(3),radius,modul,x2,y2,z2,tmpvect1(3),mod2,tmp2
        real tmpvect2(3),xc(3),xd(3),xp(3),alpha,tan2,dot,modx,mody
        real vectx(3),vecty(3)
c imedia = medium number for a object

c a non-zero entry in iepsmp indicates an atom # plus 1 (to properly treat
c re-entrant mid-points later (15 Aug 93)
	logical*1 idebmap(igrid,igrid,igrid)
	logical itobig,itest2,ipore
        write(6,*)'Starting creating Vand der Waals  Epsilon Map '
c e+++++++++++

        epsdim=natom+nobject+2
	iboxt=0
	radmax2=0.0
        rmid=float((igrid+1)/2)
        if (natom.gt.0) then
	do 691 ix=1,natom
	radmax2=amax1(radmax2,rad3(ix))
691	continue
c b+++++++++++++++++++++++++++++
c this is probably the best way to do it,depending on which surf. is desired
        temp=amax1(radprobe,exrad)
c e++++++++++++++++++++++++++++++
	radmax2=scale*(radmax2+temp)
	lim= 1+ radmax2
c
	limmax = 12
	itobig=.false.
	if(lim.gt.limmax) itobig=.true.
c
	if(itobig) goto 7878
	radtest= (radmax2 + 0.5*sqrt(3.0))**2
	ibox=0
	igrdc=(2*lim+1)**3
	i_ioff= memalloc(i_ioff,4*3*igrdc)
	do 692 ix=-lim,lim
	  do 693 iy=-lim,lim
	    do 694 iz=-lim,lim
	    dist=ix**2 + iy**2 + iz**2
	    dist1=dist + ix + 0.25
	    dist2=dist + iy + 0.25
	    dist3=dist + iz + 0.25
	    itest=0
	    if(dist.lt.radtest) itest=1
	    if(dist1.lt.radtest) itest=1
	    if(dist2.lt.radtest) itest=1
	    if(dist3.lt.radtest) itest=1
	    if(itest.eq.1) then
	    ibox=ibox+1
	    ioff(1,ibox)=ix
	    ioff(2,ibox)=iy
	    ioff(3,ibox)=iz
	    end if
694	continue
693	continue
692	continue
7878	continue
c b+++++++++++++++++++++++++
        endif
c set interiors in OBJECTS   
c
        do ii=1,nobject
          ipore=.false.
          strtmp=dataobject(ii,1)
          if (strtmp(1:4).ne.'is a') then
            strtmp1=dataobject(ii,2)
            read(strtmp(8:10),'(I3)')objecttype
            read(strtmp(12:14),'(I3)')imedia     
c completing iatmmed with imedia data
            iatmmed(natom+ii)=imedia
           write(6,*)"(setout) object  number and medianumber",ii,imedia
c check if object sits within limits of box and calculating ismin 
c and ismax accordingly
            exrd=exrad*scale
            temp=radprobe*scale+exrd
            do k = 1,3
              ismin(k) = (limgunit(k,1,ii)-temp - 1.)
              ismin(k) = min(ismin(k),igrid)
              ismin(k) = max(ismin(k),1)
              ismax(k) = (limgunit(k,2,ii)+temp + 1.)
              ismax(k) = min(ismax(k),igrid)
              ismax(k) = max(ismax(k),1)
            end do            

            if (objecttype.eq.1) then
c             dealing with a sphere
              read(strtmp(16:80),*)kind,xb,radius
              ipore=(kind.eq.2)
              radius=radius*scale
              radp=radius+exrd
              rad2=radius**2
              radp2=radp*radp
              xb(1)=(xb(1) -oldmid(1))*scale + rmid
              xb(2)=(xb(2) -oldmid(2))*scale + rmid
              xb(3)=(xb(3) -oldmid(3))*scale + rmid
              do ix=ismin(1),ismax(1)
              do iy=ismin(2),ismax(2)
              do iz=ismin(3),ismax(3)
                x2=(ix-xb(1))**2+0.25
                y2=(iy-xb(2))**2 
                z2=(iz-xb(3))**2
                if ((x2+y2+z2-0.25).le.radp2)
     &             idebmap(ix,iy,iz)=ipore
                if ((x2+y2+z2+ix-xb(1)).le.rad2) then
                  iepsmp(ix,iy,iz,1)=natom+1+ii+imedia*epsdim
                end if 
                if ((x2+y2+z2+iy-xb(2)).le.rad2) then
                  iepsmp(ix,iy,iz,2)=natom+1+ii+imedia*epsdim
                end if 
                if ((x2+y2+z2+iz-xb(3)).le.rad2) then
                  iepsmp(ix,iy,iz,3)=natom+1+ii+imedia*epsdim
                end if 
              end do
              end do
              end do
            end if


            if (objecttype.eq.2) then
c             dealing with a cylinder 
              read(strtmp(16:80),*)kind,xa,xb,radius
              ipore=(kind.eq.2)
              read(strtmp1,'(5f8.3)')vectz,modul,modul2
c here we work in grid units
              radius=radius*scale
              rad2=radius*radius
              radp=radius+exrd
              radp2=radp*radp
              modul=modul*scale
              modul2=modul*modul
              tmp=exrd*modul

              xb(1)=(xb(1) -oldmid(1))*scale + rmid
              xb(2)=(xb(2) -oldmid(2))*scale + rmid
              xb(3)=(xb(3) -oldmid(3))*scale + rmid
              vectz(1)=vectz(1)*scale
              vectz(2)=vectz(2)*scale
              vectz(3)=vectz(3)*scale

              do ix=ismin(1),ismax(1)
              do iy=ismin(2),ismax(2)
              do iz=ismin(3),ismax(3)
c               vectz=A-B; modul=|A-B|;tmpvect1=P-B; tmp1=(A-B)(P-B)
c               mod2=(P-B)**2; modul2=(A-B)**2, tmp=exrad*|A-B|.
                tmpvect1(1)=ix-xb(1)
                tmpvect1(2)=iy-xb(2)
                tmpvect1(3)=iz-xb(3) 
                tmp1=tmpvect1(1)*vectz(1)+tmpvect1(2)*vectz(2)
                tmp1=tmp1+tmpvect1(3)*vectz(3)
                if ((tmp1.ge.-tmp).and.(tmp1.le.modul2+tmp)) then
                 mod2=tmpvect1(1)**2+tmpvect1(2)**2+tmpvect1(3)**2
                 if((mod2-(tmp1/modul)**2).le.radp2)
     &               idebmap(ix,iy,iz)=ipore
                end if

                tmpvect1(1)=ix+.5-xb(1)
                tmp1=tmpvect1(1)*vectz(1)+tmpvect1(2)*vectz(2)
                tmp1=tmp1+tmpvect1(3)*vectz(3)
                if ((tmp1.ge.0.0).and.(tmp1.le.modul2)) then
                   mod2=tmpvect1(1)**2+tmpvect1(2)**2+tmpvect1(3)**2
                   if ((mod2-(tmp1/modul)**2).le.rad2) then
                      iepsmp(ix,iy,iz,1)=natom+1+ii+imedia*epsdim
                   end if
                end if

                tmpvect1(1)=ix-xb(1)
                tmpvect1(2)=iy+.5-xb(2)
                tmp1=tmpvect1(1)*vectz(1)+tmpvect1(2)*vectz(2)
                tmp1=tmp1+tmpvect1(3)*vectz(3)
                if ((tmp1.ge.0.0).and.(tmp1.le.modul2)) then
                   mod2=tmpvect1(1)**2+tmpvect1(2)**2+tmpvect1(3)**2
                   if ((mod2-(tmp1/modul)**2).le.rad2) then
                      iepsmp(ix,iy,iz,2)=natom+1+ii+imedia*epsdim
                   end if
                end if

                tmpvect1(2)=iy-xb(2)
                tmpvect1(3)=iz+.5-xb(3)
                tmp1=tmpvect1(1)*vectz(1)+tmpvect1(2)*vectz(2)
                tmp1=tmp1+tmpvect1(3)*vectz(3)
                if ((tmp1.ge.0.0).and.(tmp1.le.modul2)) then
                   mod2=tmpvect1(1)**2+tmpvect1(2)**2+tmpvect1(3)**2
                   if ((mod2-(tmp1/modul)**2).le.rad2) then
                      iepsmp(ix,iy,iz,3)=natom+1+ii+imedia*epsdim
                   end if
                end if

              end do
              end do
              end do
            end if

            if (objecttype.eq.3) then
c             dealing with a cone     
              read(strtmp(16:80),*)kind,xa,xb,alpha 
              ipore=(kind.eq.2)
c conversion degrees --> radiants
              alpha=alpha*3.1415/180
              tan2=tan(alpha)**2
              read(strtmp1,'(5f8.3)')vectz,modul,modul2
c here we work in grid units
              modul=modul*scale
              modul2=modul*modul
              xb(1)=(xb(1) -oldmid(1))*scale + rmid
              xb(2)=(xb(2) -oldmid(2))*scale + rmid
              xb(3)=(xb(3) -oldmid(3))*scale + rmid
              vectz(1)=vectz(1)*scale
              vectz(2)=vectz(2)*scale
              vectz(3)=vectz(3)*scale


              do ix=ismin(1),ismax(1)
              do iy=ismin(2),ismax(2)
              do iz=ismin(3),ismax(3)
                tmpvect1(1)=(ix-rmid)/scale +oldmid(1)
                tmpvect1(2)=(iy-rmid)/scale +oldmid(2)
                tmpvect1(3)=(iz-rmid)/scale +oldmid(3)
                call distobj(tmpvect1,dx,dy,dz,nobject,ii,exrad,dist
     &  ,.true.,zeta,axdist)
                if (dist.le.0.0) idebmap(ix,iy,iz)=ipore

c               vectz=A-B; tmpvect1=P-B; tmp1=(A-B)(P-B)
c               mod2=(P-B)**2; modul2=(A-B)**2.
                tmpvect1(1)=ix+.5-xb(1)
                tmpvect1(2)=iy-xb(2)
                tmpvect1(3)=iz-xb(3)
                tmp1=tmpvect1(1)*vectz(1)+tmpvect1(2)*vectz(2)
                tmp1=tmp1+tmpvect1(3)*vectz(3)
                if ((tmp1.ge.0.0).and.(tmp1.le.modul2)) then
                   mod2=tmpvect1(1)**2+tmpvect1(2)**2+tmpvect1(3)**2
                   tmp2=(1+tan2)*tmp1*tmp1/modul2+tan2*(modul2-2*tmp1)
                   if (mod2.le.tmp2) then
                      iepsmp(ix,iy,iz,1)=natom+1+ii+imedia*epsdim
                   end if
                end if

                tmpvect1(1)=ix-xb(1)
                tmpvect1(2)=iy+.5-xb(2)
                tmp1=tmpvect1(1)*vectz(1)+tmpvect1(2)*vectz(2)
                tmp1=tmp1+tmpvect1(3)*vectz(3)
                if ((tmp1.ge.0.0).and.(tmp1.le.modul2)) then
                   mod2=tmpvect1(1)**2+tmpvect1(2)**2+tmpvect1(3)**2
                   tmp2=(1+tan2)*tmp1*tmp1/modul2+tan2*(modul2-2*tmp1)
                   if (mod2.le.tmp2) then
                      iepsmp(ix,iy,iz,2)=natom+1+ii+imedia*epsdim
                   end if
                end if

                tmpvect1(2)=iy-xb(2)
                tmpvect1(3)=iz+.5-xb(3)
                tmp1=tmpvect1(1)*vectz(1)+tmpvect1(2)*vectz(2)
                tmp1=tmp1+tmpvect1(3)*vectz(3)
                if ((tmp1.ge.0.0).and.(tmp1.le.modul2)) then
                   mod2=tmpvect1(1)**2+tmpvect1(2)**2+tmpvect1(3)**2
                   tmp2=(1+tan2)*tmp1*tmp1/modul2+tan2*(modul2-2*tmp1)
                   if (mod2.le.tmp2) then
                      iepsmp(ix,iy,iz,3)=natom+1+ii+imedia*epsdim
                   end if
                end if

              end do
              end do
              end do
            end if

            if (objecttype.eq.4) then
c             dealing with a parallelepiped
              read(strtmp(16:80),*)kind,xa,xb,xc,xd 
              ipore=(kind.eq.2)
              read(strtmp1,'(12f6.2)')vectz,modul,vecty,mody,vectx,
     &  modx

c             conversion to axial symmetry points
              call addvect(xc,xb,tmpvect)
              call mul(0.5,tmpvect,xb)

              xb(1)=(xb(1) -oldmid(1))*scale + rmid
              xb(2)=(xb(2) -oldmid(2))*scale + rmid
              xb(3)=(xb(3) -oldmid(3))*scale + rmid

              modul=modul*scale
              modul2=modul*modul
              vectz(1)=vectz(1)*scale
              vectz(2)=vectz(2)*scale
              vectz(3)=vectz(3)*scale

              modx=modx*scale
              tmp1=modx*modx/2.
              vectx(1)=vectx(1)*scale
              vectx(2)=vectx(2)*scale
              vectx(3)=vectx(3)*scale

              mody=mody*scale
              tmp2=mody*mody/2.
              vecty(1)=vecty(1)*scale
              vecty(2)=vecty(2)*scale
              vecty(3)=vecty(3)*scale

              do ix=ismin(1),ismax(1)
              do iy=ismin(2),ismax(2)
              do iz=ismin(3),ismax(3)

c             vectz=A-B;vectx=C-D;vecty=(C+D)/2-B;tmp1=|C-D|/2   
c             modul2=(A-B)**2, tmp2=mody/2
c             dot=(P-B)(..-..); 
                xp(1)=(ix-rmid)/scale +oldmid(1)
                xp(2)=(iy-rmid)/scale +oldmid(2)
                xp(3)=(iz-rmid)/scale +oldmid(3)
                call distobj(xp,dx,dy,dz,nobject,ii,exrad,dist
     &  ,.true.,zeta,axdist)
                if (dist.le.0.0) idebmap(ix,iy,iz)=ipore

c now xp=P-B;
                xp(1)=ix+.5-xb(1)
                xp(2)=iy-xb(2)
                xp(3)=iz-xb(3)
                dot=vectz(1)*xp(1)+vectz(2)*xp(2)+vectz(3)*xp(3)
                if ((dot.ge.0.0).and.(dot.le.modul2)) then
               dot=vectx(1)*xp(1)+vectx(2)*xp(2)+vectx(3)*xp(3)
                 if (abs(dot).le.tmp1) then
               dot=vecty(1)*xp(1)+vecty(2)*xp(2)+vecty(3)*xp(3)
                  if (abs(dot).le.tmp2) then
                    iepsmp(ix,iy,iz,1)=natom+1+ii+imedia*epsdim
                  end if
                 end if
                end if

                xp(1)=ix-xb(1)
                xp(2)=iy+.5-xb(2)
                xp(3)=iz-xb(3)
                dot=vectz(1)*xp(1)+vectz(2)*xp(2)+vectz(3)*xp(3)
                if ((dot.ge.0.0).and.(dot.le.modul2)) then
               dot=vectx(1)*xp(1)+vectx(2)*xp(2)+vectx(3)*xp(3)
                 if (abs(dot).le.tmp1) then
               dot=vecty(1)*xp(1)+vecty(2)*xp(2)+vecty(3)*xp(3) 
                  if (abs(dot).le.tmp2) then
                    iepsmp(ix,iy,iz,2)=natom+1+ii+imedia*epsdim
                  end if
                 end if
                end if

                xp(1)=ix-xb(1)
                xp(2)=iy-xb(2)
                xp(3)=iz+.5-xb(3)
                dot=vectz(1)*xp(1)+vectz(2)*xp(2)+vectz(3)*xp(3)
                if ((dot.ge.0.0).and.(dot.le.modul2)) then
               dot=vectx(1)*xp(1)+vectx(2)*xp(2)+vectx(3)*xp(3)
                 if (abs(dot).le.tmp1) then
                dot=vecty(1)*xp(1)+vecty(2)*xp(2)+vecty(3)*xp(3)
                  if (abs(dot).le.tmp2) then
                    iepsmp(ix,iy,iz,3)=natom+1+ii+imedia*epsdim
                  end if
                 end if
                end if

              end do
              end do
              end do
            end if

          end if
        end do
c
c end of setting in OBJECTS
c e++++++++++++++++++++++++
c
c set interiors in MOLECULES
c
	do iv=1, natom
c
c restore values
c
	rad= rad3(iv)
	xn(1)=xn2(1,iv)
	xn(2)=xn2(2,iv)
	xn(3)=xn2(3,iv)
	if(rad.lt.1.e-6) goto 608
c
c scale radius to grid
c
	  rad = rad*scale
	  rad5= (rad + 0.5)**2
	  radp = rad + exrad*scale
c b++++++++++++++++++++++++++++       
	  rad = rad + radprobe*scale
c e++++++++++++++++++++++++++++
	  rad4= (rad + 0.5)**2
	  rad2 = rad*rad
	  radp2 = radp*radp
c
c set dielectric map
c
c check if sphere sits within limits of box
	itest2=.false.
        do k = 1,3
          ismin(k) = (xn(k) - radmax2 - 1.)
	  itest1=ismin(k)
	    ismin(k) = min(ismin(k),igrid)
	    ismin(k) = max(ismin(k),1)
	    if(itest1.ne.ismin(k)) itest2=.true.
          ismax(k) = (xn(k) + radmax2 + 1.)
	  itest1=ismax(k)
	    ismax(k) = min(ismax(k),igrid)
	    ismax(k) = max(ismax(k),1)
	    if(itest1.ne.ismax(k)) itest2=.true.
	end do
c
	if(itest2.or.itobig) then
c slow method
	num=num+1
	rad2a = rad2 - 0.25
          do 9019 iz =  ismin(3),ismax(3)
            do 9020 iy =  ismin(2),ismax(2)
              do 9021 ix =  ismin(1),ismax(1)
                  dxyz1 = (ix - xn(1))
                  dxyz2 = (iy - xn(2))
                  dxyz3 = (iz - xn(3))
                  distsq = dxyz1**2 +dxyz2**2 +dxyz3**2
		  distsq1 = distsq + dxyz1
		  distsq2 = distsq + dxyz2
		  distsq3 = distsq + dxyz3
c b+++++++++++++++++++
                if(distsq1.lt.rad2a) then
                  iepsmp(ix,iy,iz,1)=iv+1+iatmmed(iv)*epsdim
c         write(6,*) "atomo:",iv,"mezzo:",iepsmp(ix,iy,iz,1,2),"asse 1"
                end if
                if(distsq2.lt.rad2a) then
                  iepsmp(ix,iy,iz,2)=iv+1+iatmmed(iv)*epsdim
c         write(6,*) "atomo:",iv,"mezzo:",iepsmp(ix,iy,iz,2,2),"asse 2"
                end if
                if(distsq3.lt.rad2a) then
                  iepsmp(ix,iy,iz,3)=iv+1+iatmmed(iv)*epsdim
c         write(6,*) "atomo:",iv,"mezzo:",iepsmp(ix,iy,iz,3,2),"asse 3"
                end if
c e+++++++++++++++++++
		if(distsq.lt.radp2)  idebmap(ix,iy,iz) =.false.
9021		continue
9020	    continue
9019	  continue
		else
c faster method
	rad2a = rad2 - 0.25
	ixn1=nint(xn(1))
	iyn1=nint(xn(2))
	izn1=nint(xn(3))
	fxn1=ixn1-xn(1)
	fxn2=iyn1-xn(2)
	fxn3=izn1-xn(3)
	rad2ax=rad2a-fxn1
	rad2ay=rad2a-fxn2
	rad2az=rad2a-fxn3
	do 6020 ix=-lim,lim
	temp1=ix+fxn1
	temp2=ix+fxn2
	temp3=ix+fxn3
	sq1(ix)=temp1*temp1
	sq2(ix)=temp2*temp2
	sq3(ix)=temp3*temp3
	rad2a1(ix)=rad2a-temp1
	rad2a2(ix)=rad2a-temp2
	rad2a3(ix)=rad2a-temp3
6020	continue
C$DIR NO_RECURRENCE
		  do 9024 i=1,ibox
		  i1= ioff(1,i)
		  i2= ioff(2,i)
		  i3= ioff(3,i)
		  ix=ixn1+ i1
		  iy=iyn1+ i2
		  iz=izn1+ i3
        distsq = sq1(i1) +sq2(i2) + sq3(i3)
c b+++++++++++++++++++
	if(distsq.lt.rad2a1(i1))  then
          iepsmp(ix,iy,iz,1)=iv+1+iatmmed(iv)*epsdim
c         write(6,*) "atomo:",iv," mezzo:",iepsmp(ix,iy,iz,1,2),"asse 1"
        end if
	if(distsq.lt.rad2a2(i2)) then
          iepsmp(ix,iy,iz,2)=iv+1+iatmmed(iv)*epsdim
c         write(6,*) "atomo:",iv," mezzo:",iepsmp(ix,iy,iz,2,2),"asse 2"
        end if
	if(distsq.lt.rad2a3(i3)) then
          iepsmp(ix,iy,iz,3)=iv+1+iatmmed(iv)*epsdim
c         write(6,*) "atomo:",iv," mezzo:",iepsmp(ix,iy,iz,3,2),"asse 3"
        end if 
c e++++++++++++++++++++
        if(distsq.lt.radp2)   idebmap(ix,iy,iz)=.false.
9024	continue
		end if
c
608	continue
c
c end do of atoms
	end do

	i_ioff= memalloc(i_ioff,0)
c b+++++debug+++++++++++++++++++++++++++++++
c       open(52,file='iepsmapnewfirst',form='formatted')
c       do ix=1,igrid
c         do iy=1,igrid
c           do iz=1,igrid
c              write (52,*) iepsmp(ix,(igrid+1)/2,iz,3)
c           end do
c         end do
c       end do
c       close (52)
c e++++++++++++++++++++++++++++++++++++++++++
        write(6,*)'Ending creating Vand der Waals  Epsilon Map '
	return
	end
