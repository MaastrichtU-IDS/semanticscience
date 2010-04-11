#ifdef PC
cDEC$ IF DEFINED (PC)
      recursive subroutine distobj(xp,dx,dy,dz,nobject,ii,prbrad,dist,
     &inout,zeta,axdist)
cDEC$ ELSE
#else
      subroutine distobj(xp,dx,dy,dz,nobject,ii,prbrad,dist,
     &inout,zeta,axdist)
#endif
cDEC$ END IF

c this routine calculate the outgoing normal vector onto the surface
c  (possibly extended by prbrad) 
c be careful, dist is an oriented distance!!supposed to be positive 
c if the point is external to the object
c in this context, the vector d is (G-H)/dist
c where G is the point and H its projection onto the surface
c   (Walter, last update August 5, 2001) 

      include 'pointer.h'

      integer nobject,count,objecttype,ii,sign
      logical inout,imovepoint
      character*80 dataobject(nobject,2)
      character*80 strtmp,strtmp1
      real xb(3),xa(3),tmp,radius,vectz(3),vectx(3),vecty(3),
     &  alpha,xc(3),xd(3),modul2,modx,mody,prx,pry,prz,tmp1,tmp2
      real xp(3),prbrad,dist,modul,zeta,axdist,dot,talpha,pntsh,tet
    
      imovepoint=.false.
c       inout is option to calculate only dist and not dx,dy,dz
      strtmp=dataobject(ii,1)
      strtmp1=dataobject(ii,2)
      read(strtmp(8:10),'(I3)')objecttype
c     write(6,*)'objectype',strtmp

      if (objecttype.eq.1) then
c sphere
         read(strtmp(20:80),*)xb,radius
         dx=xp(1)-xb(1)
         dy=xp(2)-xb(2)
         dz=xp(3)-xb(3)
         tmp=dx*dx+dy*dy+dz*dz
         if (tmp.eq.0.) then 
c      point exactly in the center
           imovepoint=.true.
           goto 888
         end if
         tmp1=sqrt(tmp)
         dist=tmp1-radius-prbrad
         if (.not.inout) then
            dx=dx/tmp1
            dy=dy/tmp1
            dz=dz/tmp1
         end if
      else
      if (objecttype.eq.2) then
c cylinder
         read(strtmp(20:80),*)xa,xb,radius
         read(strtmp1,'(5f8.3)')vectz,modul,modul2
          
         dx=xp(1)-xb(1)
         dy=xp(2)-xb(2)
         dz=xp(3)-xb(3)
c dot=(P-B)(A-B)
         dot=dx*vectz(1)+dy*vectz(2)+dz*vectz(3)
         zeta=dot/modul
c tmp=|P-B|**2
         tmp=(dx*dx+dy*dy+dz*dz)
c axdist is |P-B|sin(teta)
         axdist=sqrt(tmp-zeta*zeta)

         dist=-prbrad-zeta
         if (.not.inout) then
            if (dist.ge.0.) then
c            inferiore
               if (axdist.gt.radius+prbrad) then
c               laterale inferiore
                  tmp1=(radius+prbrad)/axdist
                  tmp2=(prbrad+zeta*tmp1)/modul
                  dx=dx*(1-tmp1)+vectz(1)*tmp2
                  dy=dy*(1-tmp1)+vectz(2)*tmp2
                  dz=dz*(1-tmp1)+vectz(3)*tmp2
                  dist=sqrt(dx*dx+dy*dy+dz*dz)
                  dx=dx/dist
                  dy=dy/dist
                  dz=dz/dist
               else
c               assiale inferiore
                  dx=-vectz(1)/modul
                  dy=-vectz(2)/modul
                  dz=-vectz(3)/modul
               end if
            else
               dist=zeta-(modul+prbrad)
               if (dist.ge.0.) then
c            superiore
                  if (axdist.gt.radius+prbrad) then
c            laterale superiore
                     tmp1=(radius+prbrad)/axdist
                     tmp2=(-prbrad+zeta*tmp1)/modul-1.
                     dx=dx*(1-tmp1)+vectz(1)*tmp2
                     dy=dy*(1-tmp1)+vectz(2)*tmp2
                     dz=dz*(1-tmp1)+vectz(3)*tmp2
                     dist=sqrt(dx*dx+dy*dy+dz*dz)
                     dx=dx/dist
                     dy=dy/dist
                     dz=dz/dist
                  else
c            assiale superiore
                     dx=vectz(1)/modul
                     dy=vectz(2)/modul
                     dz=vectz(3)/modul
                  end if
               else
c            z-centrale
                  tmp1=axdist-radius-prbrad
                  if(tmp1.lt.dist.or.tmp1.lt.-prbrad-zeta) then
c               vicini alle basi da dentro
                     if (-dist.le.zeta+prbrad) then
c                  base superiore
                        dx=vectz(1)/modul
                        dy=vectz(2)/modul
                        dz=vectz(3)/modul
                     else
c                  base inferiore
                        dist=-zeta-prbrad
                        dx=-vectz(1)/modul
                        dy=-vectz(2)/modul
                        dz=-vectz(3)/modul
                     end if
                  else
c               vicino ai lati, da dentro o da fuori
                    if (axdist.eq.0.) then
c                       point exactly onto the axis
                       imovepoint=.true.
                       goto 888
                    end if
                    dist=tmp1
                    tmp2=zeta/modul                   
                    dx=(dx-vectz(1)*tmp2)/axdist
                    dy=(dy-vectz(2)*tmp2)/axdist
                    dz=(dz-vectz(3)*tmp2)/axdist
                  end if
               end if
            end if
         else
c -------------------------------------------------------------------
            if (dist.ge.0.) then
c            inferiore, assiale inf. gia' a posto
               if (axdist.gt.radius+prbrad) then
c               laterale inferiore
                  tmp1=(radius+prbrad)/axdist
                  tmp2=(prbrad+zeta*tmp1)/modul
                  dx=dx*(1-tmp1)+vectz(1)*tmp2
                  dy=dy*(1-tmp1)+vectz(2)*tmp2
                  dz=dz*(1-tmp1)+vectz(3)*tmp2
                  dist=sqrt(dx*dx+dy*dy+dz*dz)
               end if
            else
               dist=zeta-(modul+prbrad)
               if (dist.ge.0.) then
c            superiore
                  if (axdist.gt.radius+prbrad) then
c               laterale superiore, assiale gia' a posto
                     tmp1=(radius+prbrad)/axdist
                     tmp2=(-prbrad+zeta*tmp1)/modul-1.
                     dx=dx*(1-tmp1)+vectz(1)*tmp2
                     dy=dy*(1-tmp1)+vectz(2)*tmp2
                     dz=dz*(1-tmp1)+vectz(3)*tmp2
                     dist=sqrt(dx*dx+dy*dy+dz*dz)
                  end if
               else
c            z-centrale
                  tmp1=axdist-radius-prbrad
                  if(tmp1.lt.dist.or.tmp1.lt.-prbrad-zeta) then
c               vicini alle basi da dentro, base sup. gia' a posto
                     if (-dist.gt.zeta+prbrad) dist=-zeta-prbrad
c               base inferiore
                  else
c               vicino ai lati, da dentro o da fuori
                     dist=tmp1
                  end if
               end if
            end if
         end if
c -------------------------------------------------------------------
      else
c else di object type 2
      if (objecttype.eq.3) then
c cone
         read(strtmp(20:80),*)xa,xb,alpha
c conversion degrees --> radiants
         alpha=alpha*3.1415/180
         talpha=tan(alpha)
            read(strtmp1,'(5f8.3)')vectz,modul,modul2
         radius=(modul+2.*prbrad)*talpha
c         radius=extended radius of the cone
          
            dx=xp(1)-xb(1)
            dy=xp(2)-xb(2)
            dz=xp(3)-xb(3)
c dot=(P-B)(A-B)
            dot=dx*vectz(1)+dy*vectz(2)+dz*vectz(3)
            zeta=dot/modul
c tmp=|P-B|**2
            tmp=(dx*dx+dy*dy+dz*dz)
c axdist is |P-B|sin(teta)
            axdist=sqrt(tmp-zeta*zeta)
         if (.not.inout) then

            tmp1=zeta+prbrad
           if(tmp1.le.0.or.zeta.le.(axdist-radius)*talpha-prbrad)then
               if (axdist.le.radius) then
c exactly below the basis
                  dist=-tmp1
                  dx=-vectz(1)/modul
                  dy=-vectz(2)/modul
                  dz=-vectz(3)/modul
               else
c laterally below faces
                  tmp1=radius/axdist
                  tmp2=(prbrad+zeta*tmp1)/modul
                  dx=dx*(1-tmp1)+vectz(1)*tmp2
                  dy=dy*(1-tmp1)+vectz(2)*tmp2
                  dz=dz*(1-tmp1)+vectz(3)*tmp2
                  dist=sqrt(dx*dx+dy*dy+dz*dz)
                  dx=dx/dist
                  dy=dy/dist
                  dz=dz/dist
               end if
            else
               tmp1=zeta-modul-prbrad
               if(tmp1/sqrt(axdist**2+tmp1**2).gt.sin(alpha))then
c beyond the tip
                  tmp2=(1+prbrad/modul)     
                  dx=dx-tmp2*vectz(1)
                  dy=dy-tmp2*vectz(2)
                  dz=dz-tmp2*vectz(3)
                  dist=sqrt(dx*dx+dy*dy+dz*dz)
                  if (.not.inout) then
                    if (dist.eq.0.) goto 888
                    dx=dx/dist
                    dy=dy/dist
                    dz=dz/dist
                  end if
               else
c facing the lateral or internal             
                  dist=-prbrad-zeta
                  tmp2=axdist*cos(alpha)+tmp1*sin(alpha) 
                  if (tmp2.gt.dist)then
c facing lateral
                     dist=tmp2
                     if (axdist.eq.0.) then
c                     point exactly onto the axis
                        imovepoint=.true.
                        goto 888
                     end if
                     tmp1=cos(alpha)/axdist
                     tmp2=tmp1*(axdist*talpha-zeta)/modul
                     dx=tmp1*dx+tmp2*vectz(1)
                     dy=tmp1*dy+tmp2*vectz(2)
                     dz=tmp1*dz+tmp2*vectz(3)
                  else
c internal and closest to the basis
                     tmp=-1./modul
                     dx=vectz(1)*tmp
                     dy=vectz(2)*tmp
                     dz=vectz(3)*tmp
                  end if
               end if
            end if
c ----------------------------------------------------------------------
         else
            tmp1=zeta+prbrad
           if(tmp1.le.0.or.zeta.le.(axdist-radius)*talpha-prbrad)then
               if (axdist.le.radius) then
c exactly below the basis
                  dist=-tmp1
               else
c laterally below faces
                  tmp1=radius/axdist
                  tmp2=(prbrad+zeta*tmp1)/modul
                  dx=dx*(1-tmp1)+vectz(1)*tmp2
                  dy=dy*(1-tmp1)+vectz(2)*tmp2
                  dz=dz*(1-tmp1)+vectz(3)*tmp2
                  dist=sqrt(dx*dx+dy*dy+dz*dz)
               end if
            else
               tmp1=zeta-modul-prbrad
               if(tmp1/sqrt(axdist**2+tmp1**2).gt.sin(alpha))then
c beyond the tip
                  tmp2=(1+prbrad/modul)     
                  dx=dx-tmp2*vectz(1)
                  dy=dy-tmp2*vectz(2)
                  dz=dz-tmp2*vectz(3)
                  dist=sqrt(dx*dx+dy*dy+dz*dz)
               else
c facing the lateral or internal             
                  dist=-prbrad-zeta
                  tmp2=axdist*cos(alpha)+tmp1*sin(alpha) 
                  if (abs(tmp2).lt.abs(dist)) dist=tmp2
c facing lateral
               end if
            end if
         end if

c   -------------------------------------------------------------------
      else
c else di objecttype 3
         if(objecttype.eq.4) then
c box
            read(strtmp(20:80),*)xa,xb,xc,xd
               read(strtmp1,'(12f6.2)')vectz,modul,vecty,mody,vectx,
     &  modx
c normalize vectors
               do i=1,3
                 vectx(i)=vectx(i)/modx
                 vecty(i)=vecty(i)/mody
                 vectz(i)=vectz(i)/modul
               end do
c calulate projections
               dx=xp(1)-xa(1)
               dy=xp(2)-xa(2)
               dz=xp(3)-xa(3)
c dot=(P-A)(D-A) new notation
               dot=dx*vectz(1)+dy*vectz(2)+dz*vectz(3)
               prz=dot
c dot=(P-A)(C-A) new notation
               dot=dx*vecty(1)+dy*vecty(2)+dz*vecty(3)
               pry=dot
c dot=(P-A)(B-A) new notation
               dot=dx*vectx(1)+dy*vectx(2)+dz*vectx(3)
               prx=dot
c calculate components of the projection of P onto the extended surface
c change temporarily modulus values only for convenience
               modx=modx+prbrad
               mody=mody+prbrad
               modul=modul+prbrad
               sign=1
               if(prx.le.-prbrad) then 
               prx=-prbrad
                  sign=0
               else
                  if(prx.ge.modx) then
                  prx=modx
                     sign=0
                  end if
               end if
               if(pry.le.-prbrad) then
               pry=-prbrad
                  sign=0
               else
                  if(pry.ge.mody) then
                  pry=mody
                  sign=0
                  end if
               end if
               if(prz.le.-prbrad) then
               prz=-prbrad
                  sign=0
               else
               if(prz.ge.modul) then
                  prz=modul
                     sign=0
                  end if
               end if
c now if sign=1 we are inside the box so dist will eventually be negative
               if (sign.eq.1) then
               i=1
                  dist=prx+prbrad
                  if (prx+prbrad.gt.modx-prx) then
                  i=-1
                     dist=modx-prx
                  end if
                  if (pry+prbrad.lt.dist) then
                  i=2
                     dist=pry+prbrad
                  end if
                  if (mody-pry.lt.dist) then
                  i=-2
                     dist=mody-pry
                  end if
                  if (prz+prbrad.lt.dist) then
                     i=3
                     dist=prz+prbrad
                  end if
                  if (modul-prz.lt.dist) then
                     i=-3
                     dist=modul-prz
                  end if
                  dist=-dist
c                 i moduli li lascio sbagliati perche' non li riuso
c                 mody=mody-prbrad
c                 modul=modul-prbrad
                  if(inout) go to 90
                  go to(20,30,40,50,60,70,80) i+4
50                continue
                  write(6,*)'problems in distobject'
                  stop
20                continue
                     dx=vectz(1)
                     dy=vectz(2)
                     dz=vectz(3)
                     go to 90
30                continue
                     dx=vecty(1)
                     dy=vecty(2)
                     dz=vecty(3)
                     go to 90
40                continue
                     dx=vectx(1)
                     dy=vectx(2)
                     dz=vectx(3)
                     go to 90
60                continue
                     dx=-vectx(1)
                     dy=-vectx(2)
                     dz=-vectx(3)
                     go to 90
70                continue
                     dx=-vecty(1)
                     dy=-vecty(2)
                     dz=-vecty(3)
                     go to 90
80                continue
                     dx=-vectz(1)
                     dy=-vectz(2)
                     dz=-vectz(3)
90                continue
            else    
c                 i moduli li lascio sbagliati perche' non li riuso
c                 modx=modx-prbrad
c                 mody=mody-prbrad
c                 modul=modul-prbrad
                  prx=prx
                  pry=pry
                  prz=prz
                  dx=prx*vectx(1)+pry*vecty(1)+prz*vectz(1)-dx
                  dy=prx*vectx(2)+pry*vecty(2)+prz*vectz(2)-dy
                  dz=prx*vectx(3)+pry*vecty(3)+prz*vectz(3)-dz
                  dist=dx*dx+dy*dy+dz*dz
                  if (.not.inout) then
                    if (dist.eq.0.) goto 888
                    dist=sqrt(dist)
                    dx=-dx/dist
                    dy=-dy/dist
                    dz=-dz/dist
                  end if
            end if
         end if
      end if 
      end if
      end if
      goto 999

888   continue

c   bgp lies on extended surface or center or axdist=0, correcting 
      pntsh=0.
      if (imovepoint) then
         pntsh=1.e-5
         if (vectz(2).eq.0.) tet=1.5707963268
         else tet=atan(vectz(3)/vectz(2))
         xp(2)=xp(2)+pntsh*sin(tet)
         xp(3)=xp(3)+pntsh*cos(tet)
      end if
      call distobj(xp,dx,dy,dz,nobject,ii,prbrad+1.e-5-pntsh,dist,inout
     &,zeta,axdist)
      if (.not.imovepoint) dist=0.0

999   continue

      return
      end

