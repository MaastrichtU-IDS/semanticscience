        subroutine distrTOpoint(igrid,scale,ncrgmx,ndistr,
     &  ic1,cmid,natom)

        include "pointer.h"
c
        dimension atmcrg(4,ncrgmx),chgpos(3,ncrgmx)
        integer ndistr,ic1,nteta,nfi,ntetamax
        character*80 datadistr(ndistr)
        character*80 strtmp
c linkobj=number of object which is thought to contain the charge
        integer crgatn(1),natom,linkobj,crgatnval
        real xb(3),xa(3),xu(3),xv(3),xw(3),tmpvect(3),xc(3),xd(3)
c charge = total charge in distribution, as a fraction of e
        real charge,pi,tmp,tmp1,tmp2,radius,scale,modul,tn,tv
        real fractcharge,ro,nt,tanalpha,cmid(3),crgassigned,nrof
        real fractcharge1,xm(3),au,av,aw,deltau,deltav,deltaw
        real h,ucurr,vcurr,xp(3),nro
        real lls,lll,ll,ls,dllvol,dlllin,dlsvol,dlslin,rad,tt,teta

        pi=3.1416
        h=1./scale
        rmid=float((igrid+1)/2)
        write(6,*) "number of charge distrib. present ",ndistr 

        do i=1,ndistr
        strtmp=datadistr(i)
        read(strtmp(14:16),*)linkobj
        crgatnval=-i
        if (linkobj.gt.0) crgatnval=natom+linkobj
        read(strtmp(18:23),*)charge

        if (strtmp(8:10).eq.'  1') then
c here we have a spherical distribution
          read(strtmp(27:80),*)xb,radius

c         if (strtmp(11:12).eq.' v') then
c         uniform in the volume
c         tmp=scale*scale*scale*radius*radius*radius
c         fractcharge=3*charge/(4*pi*tmp)
c         do nro=1,radius*scale
c         do nteta=1,pi*nro
c         tmp=nro*sin(nteta/nro)
c         do nfi=1,2*pi*tmp
c          ic1=ic1+1
c          chgpos(1,ic1)=xb(1)+tmp*cos(nfi/tmp)/scale 
c          chgpos(2,ic1)=xb(2)+tmp*sin(nfi/tmp)/scale
c          chgpos(3,ic1)=xb(3)+nro*cos(nteta/nro)/scale
c          atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
c          atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
c          atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
c          atmcrg(4,ic1)=fractcharge
c          crgatn(ic1)=crgatnval
c         end do
c         end do
c         end do
c         endif
c the new version,improved, needs less charges to fill the object
          if (strtmp(11:12).eq.' v') then
c         uniform in the volume
          crgassigned=0.0
          tmp=scale*scale*scale*radius*radius*radius
          fractcharge1=3*charge/(4*pi*tmp)
          tmp=radius*scale
          do nro=0,int(sqrt(2*tmp)-1.0)
          ncell=ic1
c         tmp1=current radius*scale=1/deltateta
          tmp1=(tmp-.5*(nro+1)*(nro+1))
          fractcharge=fractcharge1*(nro+1)*2*sin(1/(2*tmp1))*(tmp1+
     &  (nro+1)*(nro+1)/(12*tmp1))
          write(6,*)"distrib: ro:",tmp1/scale
          do nteta=0,(pi*tmp1-.5)
c         tmp2=1/deltaphi
          tmp2=tmp1*sin((.5+nteta)/tmp1)
          do nfi=0,2*pi*tmp2-.5
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)+tmp2*cos((nfi+.5)/tmp2)/scale
           chgpos(2,ic1)=xb(2)+tmp2*sin((nfi+.5)/tmp2)/scale
           chgpos(3,ic1)=xb(3)+tmp1*cos((nteta+.5)/tmp1)/scale
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=fractcharge
           crgatn(ic1)=crgatnval
          end do
          end do
          crgassigned=crgassigned+fractcharge*(ic1-ncell)
          end do
          if (abs(charge-crgassigned).gt.1.e-6) then
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)
           chgpos(2,ic1)=xb(2)
           chgpos(3,ic1)=xb(3)
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=charge-crgassigned
           crgatn(ic1)=crgatnval
           if(fractcharge*charge.lt.0.)write(6,*)"WARNING fc*charge<0!"
           write(6,*)"charge not uniformly assigned:",charge-crgassigned
          end if
          endif

          if (strtmp(11:12).eq.' s') then
c         uniform on the surface
          tmp=scale*scale*radius*radius
          fractcharge=charge/(4*pi*tmp)
          ro=radius*scale
          do nteta=1,pi*ro
          tmp=ro*sin(nteta/ro)
          do nfi=1,2*pi*tmp
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)+tmp*cos(nfi/tmp)/scale
           chgpos(2,ic1)=xb(2)+tmp*sin(nfi/tmp)/scale
           chgpos(3,ic1)=xb(3)+radius*cos(nteta/ro)
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=fractcharge
           crgatn(ic1)=crgatnval
          end do
          end do
          endif
        endif

        if (strtmp(8:10).eq.'  2') then
c here we have a cylindric distribution
          read(strtmp(27:80),*)xa,xb,radius
          call basisortho(xa,xb,xu,xv,xw,modul)

          if (strtmp(11:12).eq.' v') then
c           uniform in the volume
c           tmp=scale*scale*scale*radius*radius*modul
c           fractcharge=charge/(pi*tmp)
c           tmp1=radius*scale-.5
c           deltanro=tmp1/int(tmp1)
c           do nro=tmp1,0,-deltanro
c            do nteta=1,2*pi*nro
c             tmp=nro*sin(float(nteta)/nro)
c             tmp1=nro*cos(float(nteta)/nro)
c             do nt=.5,scale*modul-.5
c              fractcharge=fract/
c              ic1=ic1+1
c              chgpos(1,ic1)=xb(1)+(tmp1*xu(1)+tmp*xv(1)+nt*xw(1))*h
c              chgpos(2,ic1)=xb(2)+(tmp1*xu(2)+tmp*xv(2)+nt*xw(2))*h
c              chgpos(3,ic1)=xb(3)+(           tmp*xv(3)+nt*xw(3))*h
c              atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
c              atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
c              atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
c              atmcrg(4,ic1)=fractcharge
c              crgatn(ic1)=crgatnval
c             end do
c            end do
c           end do
c           write(6,*)nro,nteta,nt

c the new version,improved, needs less charges to fill the object
          xp(1)=(xa(1)+xb(1))*.5
          xp(2)=(xa(2)+xb(2))*.5
          xp(3)=(xa(3)+xb(3))*.5
          tmp1=radius*radius*modul
          fract=charge/(pi*tmp1)
          rho=radius-.5*h
          drhovol=h
          ttmax=.5*(modul-h)
          tt=ttmax
          dttvol=h
100       continue
            ntetamax=2*pi*rho*scale
            if (ntetamax.ne.0) then
            do nteta=1,ntetamax
              dtetavol=2.*pi/ntetamax
              teta=nteta*dtetavol
              tmp1=rho*cos(teta)
              tmp2=rho*sin(teta)
              fractcharge=fract*rho*drhovol*dtetavol*dttvol
              if (tt.eq.0.) fractcharge=2.*fractcharge 

              ic1=ic1+1
              chgpos(1,ic1)=xp(1)+(tmp1*xu(1)+tmp2*xv(1))+tt*xw(1)
              chgpos(2,ic1)=xp(2)+(tmp1*xu(2)+tmp2*xv(2))+tt*xw(2)
              chgpos(3,ic1)=xp(3)+            tmp2*xv(3)+tt*xw(3)
              atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
              atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
              atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
              atmcrg(4,ic1)=fractcharge
              crgatn(ic1)=crgatnval

              if (tt.gt.0.) then
                ic1=ic1+1
                chgpos(1,ic1)=chgpos(1,ic1-1)-2.*tt*xw(1)
                chgpos(2,ic1)=chgpos(2,ic1-1)-2.*tt*xw(2)
                chgpos(3,ic1)=chgpos(3,ic1-1)-2.*tt*xw(3)
                atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
                atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
                atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
                atmcrg(4,ic1)=fractcharge
                crgatn(ic1)=crgatnval
              end if

            end do
            else
              if (tt.gt.0.) then
                ic1=ic1+1
                chgpos(1,ic1)=xp(1)-tt*xw(1)
                chgpos(2,ic1)=xp(2)-tt*xw(2)
                chgpos(3,ic1)=xp(3)-tt*xw(3)
                atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
                atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
                atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
                atmcrg(4,ic1)=pi*fract*drhovol*drhovol*dttvol
                crgatn(ic1)=crgatnval
              else
                dttvol=2.*dttvol
              end if

              ic1=ic1+1
              chgpos(1,ic1)=xp(1)+tt*xw(1)
              chgpos(2,ic1)=xp(2)+tt*xw(2)
              chgpos(3,ic1)=xp(3)+tt*xw(3)
              atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
              atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
              atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
              atmcrg(4,ic1)=pi*fract*drhovol*drhovol*dttvol
              crgatn(ic1)=crgatnval
            end if
            tt=tt-.5*dttvol
            dttvol=amin1(drhovol,dttvol+.5*h)
            tt=tt-.5*dttvol
            if (tt.gt.-.5*dttvol) then
              if (tt.lt..5*dttvol) then
                dttvol=tt+.5*dttvol
                tt=0.0
              end if
              go to 100
            end if
            tt=ttmax
            dttvol=h
            rho=rho-.5*drhovol
            drhovol=drhovol+.5*h
            rho=rho-.5*drhovol
            if (rho.gt.-.5*drhovol) then
              if (rho.lt..5*drhovol) then
                drhovol=rho+.5*drhovol
                rho=0.0
              end if
              go to 100
            end if

          endif

          if (strtmp(11:12).eq.' s') then
c         uniform on the LATERAL surface
            tmp=scale*scale*radius*modul 
            fractcharge=charge/(2*pi*tmp)
            ro=radius*scale
            do nteta=1,2*pi*ro
              tmp=ro*sin(nteta/ro)
              tmp1=ro*cos(nteta/ro)
              do nt=1,modul*scale
               ic1=ic1+1
               chgpos(1,ic1)=xb(1)+(tmp1*xu(1)+tmp*xv(1)+nt*xw(1))/scale
               chgpos(2,ic1)=xb(2)+(tmp1*xu(2)+tmp*xv(2)+nt*xw(2))/scale
               chgpos(3,ic1)=xb(3)+(tmp*xv(3)+nt*xw(3))/scale
               atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
               atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
               atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
               atmcrg(4,ic1)=fractcharge
               crgatn(ic1)=crgatnval
              end do
            end do
          endif
        endif

        if (strtmp(8:10).eq.'  3') then
c here we have a conic distribution
          read(strtmp(27:80),*)xa,xb,alpha 
          alpha=alpha*3.1415/180
          call basisortho(xa,xb,xu,xv,xw,modul)
          radius=tan(alpha)*modul

          if (strtmp(11:12).eq.' v') then
c         uniform in the volume
          tmp=(scale**3)*radius*radius*modul
          fractcharge=3*charge/(pi*tmp)
          do nro=1,radius*scale
          do nteta=1,2*pi*nro
          tmp=nro*sin(float(nteta)/nro)
          tmp1=nro*cos(float(nteta)/nro)
          do nt=1,modul*(scale-nro/radius)
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)+(tmp1*xu(1)+tmp*xv(1)+nt*xw(1))/scale
           chgpos(2,ic1)=xb(2)+(tmp1*xu(2)+tmp*xv(2)+nt*xw(2))/scale
           chgpos(3,ic1)=xb(3)+(tmp*xv(3)+nt*xw(3))/scale
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=fractcharge
           crgatn(ic1)=crgatnval
          end do
          end do
          end do
          endif

          if (strtmp(11:12).eq.' s') then
c         uniform on the LATERAL surface
          tmp=scale*scale*radius*modul
          fractcharge=charge*cos(alpha)/(pi*tmp)
          do nro=1,radius*scale/sin(alpha)
          nrof=nro*sin(alpha)
          do nteta=1,2*pi*nrof
          tmp=nrof*sin(float(nteta)/nrof)
          tmp1=nrof*cos(float(nteta)/nrof)
          nt=modul*(scale-nrof/radius)
           ic1=ic1+1
           if (ic1.eq.976) then
           write(6,*)'fsfesfse'
           end if
           chgpos(1,ic1)=xb(1)+(tmp1*xu(1)+tmp*xv(1)+nt*xw(1))/scale
           chgpos(2,ic1)=xb(2)+(tmp1*xu(2)+tmp*xv(2)+nt*xw(2))/scale
           chgpos(3,ic1)=xb(3)+(tmp*xv(3)+nt*xw(3))/scale
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=fractcharge
           crgatn(ic1)=crgatnval
          end do
          end do
          endif
        endif

        if (strtmp(8:10).eq.'  4') then
c here we have a parallelepiped distribution
          read(strtmp(27:80),*)xa,xb,xc,xd 
c         conversion to axial symmetry points
          call addvect(xd,xb,tmpvect)
          call mul(0.5,tmpvect,xb)
          call diffvect(xa,xc,tmpvect)
          call addvect(tmpvect,xb,xa)

c         call diffvect(xa,xb,xw)
c         call diffvect(xc,xd,xu)
c         xv(1)=2*xb(1)-xd(1)-xc(1)
c         xv(2)=2*xb(2)-xd(2)-xc(2)
c         xv(3)=2*xb(3)-xd(3)-xc(3)
c         tmp=(A-B)**2; tmp1=(C-D)**2;tmp2=(E-D)**2 
c         now xu,xv,xw are vectors, not versors
c         call inner(xw,xw,tmp)
c         call inner(xu,xu,tmp1)
c         call inner(xv,xv,tmp2)

c         only uniform in the volume, at least for now
c         fractcharge=charge/(tmp*tmp1*tmp2*(scale**3))
c         do nt=1/(scale*tmp),1,1/(scale*tmp)
c         do tv=1/(scale*tmp2),0.5,1/(scale*tmp2)
c         do tu=1/(scale*tmp1),0.5,1/(scale*tmp1)
c          ic1=ic1+1
c          chgpos(1,ic1)=xb(1)+tu*xu(1)+tv*xv(1)+nt*xw(1)
c          chgpos(2,ic1)=xb(2)+tu*xu(2)+tv*xv(2)+nt*xw(2)               
c          chgpos(3,ic1)=xb(3)+tu*xu(3)+tv*xv(3)+nt*xw(3)           
c          atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
c          atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
c          atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
c          atmcrg(4,ic1)=fractcharge
c          crgatn(ic1)=crgatnval
c          ic1=ic1+1
c          chgpos(1,ic1)=xb(1)-tu*xu(1)+tv*xv(1)+nt*xw(1)
c          chgpos(2,ic1)=xb(2)-tu*xu(2)+tv*xv(2)+nt*xw(2)               
c          chgpos(3,ic1)=xb(3)-tu*xu(3)+tv*xv(3)+nt*xw(3)           
c          atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
c          atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
c          atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
c          atmcrg(4,ic1)=fractcharge
c          crgatn(ic1)=crgatnval
c          ic1=ic1+1
c          chgpos(1,ic1)=xb(1)+tu*xu(1)-tv*xv(1)+nt*xw(1)
c          chgpos(2,ic1)=xb(2)+tu*xu(2)-tv*xv(2)+nt*xw(2)               
c          chgpos(3,ic1)=xb(3)+tu*xu(3)-tv*xv(3)+nt*xw(3)           
c          atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
c          atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
c          atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
c          atmcrg(4,ic1)=fractcharge
c          crgatn(ic1)=crgatnval
c          ic1=ic1+1
c          chgpos(1,ic1)=xb(1)-tu*xu(1)-tv*xv(1)+nt*xw(1)
c          chgpos(2,ic1)=xb(2)-tu*xu(2)-tv*xv(2)+nt*xw(2)               
c          chgpos(3,ic1)=xb(3)-tu*xu(3)-tv*xv(3)+nt*xw(3)           
c          atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
c          atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
c          atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
c          atmcrg(4,ic1)=fractcharge
c          crgatn(ic1)=crgatnval

c 
c the new version,improved, needs less charges to fill the object
          call diffvect(xa,xb,xw)
          call diffvect(xc,xd,xu)
          xv(1)=2*xb(1)-xd(1)-xc(1)
          xv(2)=2*xb(2)-xd(2)-xc(2)
          xv(3)=2*xb(3)-xd(3)-xc(3)
c         at this moment
c         tmp=(A-B)**2; tmp1=(C-D)**2;tmp2=(E-D)**2
          call inner(xw,xw,tmp)
          tmp =sqrt(tmp)
          call inner(xu,xu,tmp1)
          tmp1 =sqrt(tmp1)
          call inner(xv,xv,tmp2)
          tmp2 =sqrt(tmp2)

c ordering by lenght
          if (tmp2.lt.tmp1) call swap(xv,xu,tmp2,tmp1)
          if (tmp1.lt.tmp) call swap(xu,xw,tmp1,tmp)
          if (tmp2.lt.tmp1) call swap(xv,xu,tmp2,tmp1)   

c         from now on  xu,xv are versors, xw is a vector
          call mul(1/tmp1,xu,xu)
          call mul(1/tmp2,xv,xv)


c xm = middle point between xa and xb
          crgassigned=0.0
          fractcharge=charge/(tmp*tmp1*tmp2)
          call addvect(xa,xb,xm)
          call mul(.5,xm,xm)
          do nt=1/sqrt(scale*tmp),1,1/sqrt(scale*tmp)
             deltaw=nt*sqrt(tmp/scale)

             deltau=1/scale
             ucurr=(tmp1+1/scale)/2
             du=deltau

1000         deltau=min(deltau,deltaw)
             du=(du+deltau)/2
             ucurr=ucurr-du
             if (ucurr.lt.0.0) go to 1030 
             
                deltav=1/scale
                vcurr=(tmp2+1/scale)/2
                dv=deltav

1010            deltav=min(deltav,deltau)
                dv=(dv+deltav)/2
                vcurr=vcurr-dv
                if (vcurr.lt.0.0) go to 1020              

               fractcharge1=fractcharge*deltau*deltav*deltaw
               ic1=ic1+1
               aw=.5*(1-nt*nt)
               chgpos(1,ic1)=xm(1)+ucurr*xu(1)+vcurr*xv(1)+aw*xw(1)
               chgpos(2,ic1)=xm(2)+ucurr*xu(2)+vcurr*xv(2)+aw*xw(2)
               chgpos(3,ic1)=xm(3)+ucurr*xu(3)+vcurr*xv(3)+aw*xw(3)
               atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
               atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
               atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
               atmcrg(4,ic1)=fractcharge1
               crgassigned=crgassigned+fractcharge1
               crgatn(ic1)=crgatnval
               ic1=ic1+1
               chgpos(1,ic1)=xm(1)+ucurr*xu(1)+vcurr*xv(1)-aw*xw(1)
               chgpos(2,ic1)=xm(2)+ucurr*xu(2)+vcurr*xv(2)-aw*xw(2)
               chgpos(3,ic1)=xm(3)+ucurr*xu(3)+vcurr*xv(3)-aw*xw(3)
               atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
               atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
               atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
               atmcrg(4,ic1)=fractcharge1
               crgassigned=crgassigned+fractcharge1
               crgatn(ic1)=crgatnval

               ic1=ic1+1
               chgpos(1,ic1)=xm(1)-ucurr*xu(1)+vcurr*xv(1)+aw*xw(1)
               chgpos(2,ic1)=xm(2)-ucurr*xu(2)+vcurr*xv(2)+aw*xw(2)
               chgpos(3,ic1)=xm(3)-ucurr*xu(3)+vcurr*xv(3)+aw*xw(3)
               atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
               atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
               atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
               atmcrg(4,ic1)=fractcharge1
               crgassigned=crgassigned+fractcharge1
               crgatn(ic1)=crgatnval
               ic1=ic1+1
               chgpos(1,ic1)=xm(1)-ucurr*xu(1)+vcurr*xv(1)-aw*xw(1)
               chgpos(2,ic1)=xm(2)-ucurr*xu(2)+vcurr*xv(2)-aw*xw(2)
               chgpos(3,ic1)=xm(3)-ucurr*xu(3)+vcurr*xv(3)-aw*xw(3)
               atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
               atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
               atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
               atmcrg(4,ic1)=fractcharge1
               crgassigned=crgassigned+fractcharge1
               crgatn(ic1)=crgatnval
    
               ic1=ic1+1
               chgpos(1,ic1)=xm(1)+ucurr*xu(1)-vcurr*xv(1)+aw*xw(1)
               chgpos(2,ic1)=xm(2)+ucurr*xu(2)-vcurr*xv(2)+aw*xw(2)
               chgpos(3,ic1)=xm(3)+ucurr*xu(3)-vcurr*xv(3)+aw*xw(3)
               atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
               atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
               atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
               atmcrg(4,ic1)=fractcharge1
               crgassigned=crgassigned+fractcharge1
               crgatn(ic1)=crgatnval
               ic1=ic1+1
               chgpos(1,ic1)=xm(1)+ucurr*xu(1)-vcurr*xv(1)-aw*xw(1)
               chgpos(2,ic1)=xm(2)+ucurr*xu(2)-vcurr*xv(2)-aw*xw(2)
               chgpos(3,ic1)=xm(3)+ucurr*xu(3)-vcurr*xv(3)-aw*xw(3)
               atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
               atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
               atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
               atmcrg(4,ic1)=fractcharge1
               crgassigned=crgassigned+fractcharge1
               crgatn(ic1)=crgatnval

               ic1=ic1+1
               chgpos(1,ic1)=xm(1)-ucurr*xu(1)-vcurr*xv(1)+aw*xw(1)
               chgpos(2,ic1)=xm(2)-ucurr*xu(2)-vcurr*xv(2)+aw*xw(2)
               chgpos(3,ic1)=xm(3)-ucurr*xu(3)-vcurr*xv(3)+aw*xw(3)
               atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
               atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
               atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
               atmcrg(4,ic1)=fractcharge1
               crgassigned=crgassigned+fractcharge1
               crgatn(ic1)=crgatnval
               ic1=ic1+1
               chgpos(1,ic1)=xm(1)-ucurr*xu(1)-vcurr*xv(1)-aw*xw(1)
               chgpos(2,ic1)=xm(2)-ucurr*xu(2)-vcurr*xv(2)-aw*xw(2)
               chgpos(3,ic1)=xm(3)-ucurr*xu(3)-vcurr*xv(3)-aw*xw(3)
               atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
               atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
               atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
               atmcrg(4,ic1)=fractcharge1
               crgassigned=crgassigned+fractcharge1
               crgatn(ic1)=crgatnval


                dv=deltav
                deltav=deltav+1/scale
                go to 1010 

1020         du=deltau
             deltau=deltau+1/scale
             go to 1000

1030         continue

         end do


          if (abs(charge-crgassigned).gt.1.e-6) then
          ic1=ic1+1
           chgpos(1,ic1)=xm(1)
           chgpos(2,ic1)=xm(2)
           chgpos(3,ic1)=xm(3)
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=charge-crgassigned
           crgatn(ic1)=crgatnval
           if(fractcharge*charge.lt.0.)write(6,*)"WARNING fc*charge<0!"
           write(6,*)"charge not uniformly assigned:",charge-crgassigned
          end if

        endif


        if (strtmp(8:10).eq.'  8') then
c here we have a discrete distribution of point charge
          read(strtmp(27:80),*)xb
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)               
           chgpos(2,ic1)=xb(2)                        
           chgpos(3,ic1)=xb(3)                            
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=charge
           crgatn(ic1)=crgatnval
        endif

        if (strtmp(8:10).eq.'  9') then
c here we have a linear  distribution
          read(strtmp(27:80),*)xa,xb
          call diffvect(xa,xb,tmpvect)
          call inner(tmpvect,tmpvect,modul)

          tmp=1.0/(scale*modul)
          fractcharge=charge*tmp
          do nt=tmp,1,tmp
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)+nt*tmpvect(1)               
           chgpos(2,ic1)=xb(2)+nt*tmpvect(2)                        
           chgpos(3,ic1)=xb(3)+nt*tmpvect(3)                            
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=fractcharge
           crgatn(ic1)=crgatnval
          end do
        endif

        if (strtmp(8:10).eq.' 10') then
c here we have a circular surface distribution
          read(strtmp(27:80),*)xa,xb,radius
          call basisortho(xa,xb,xu,xv,xw,modul)

          tmp=scale*scale*radius*radius
          fractcharge=charge/(pi*tmp)
          do nro=1,radius*scale
          do nteta=1,2*pi*nro
           tmp=nro*sin(float(nteta)/nro)
           tmp1=nro*cos(float(nteta)/nro)
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)+(tmp1*xu(1)+tmp*xv(1))/scale
           chgpos(2,ic1)=xb(2)+(tmp1*xu(2)+tmp*xv(2))/scale
           chgpos(3,ic1)=xb(3)+(tmp*xv(3))/scale
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=fractcharge
           crgatn(ic1)=crgatnval
          end do
          end do
        endif

        if (strtmp(8:10).eq.' 11') then
c here we have a rectangular surface distribution
          read(strtmp(27:80),*)xb,xc,xd
          call diffvect(xc,xd,xu)
          xv(1)=2*xb(1)-xd(1)-xc(1)
          xv(2)=2*xb(2)-xd(2)-xc(2)
          xv(3)=2*xb(3)-xd(3)-xc(3)
c         tmp1=(C-D)**2;tmp2=(E-D)**2
c         xu=(C-D),xv=(E-D) are not necessarily unitary vectors
          call inner(xu,xu,tmp1)
          call inner(xv,xv,tmp2)

          fractcharge=charge/(tmp1*tmp2*(scale**2))
          do tv=1/(scale*tmp2),0.5,1/(scale*tmp2)
          do tu=1/(scale*tmp1),0.5,1/(scale*tmp1)
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)+tu*xu(1)+tv*xv(1)
           chgpos(2,ic1)=xb(2)+tu*xu(2)+tv*xv(2)
           chgpos(3,ic1)=xb(3)+tu*xu(3)+tv*xv(3)
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=fractcharge
           crgatn(ic1)=crgatnval
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)-tu*xu(1)+tv*xv(1)
           chgpos(2,ic1)=xb(2)-tu*xu(2)+tv*xv(2)
           chgpos(3,ic1)=xb(3)-tu*xu(3)+tv*xv(3)
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=fractcharge
           crgatn(ic1)=crgatnval
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)+tu*xu(1)-tv*xv(1)
           chgpos(2,ic1)=xb(2)+tu*xu(2)-tv*xv(2)
           chgpos(3,ic1)=xb(3)+tu*xu(3)-tv*xv(3)
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=fractcharge
           crgatn(ic1)=crgatnval
           ic1=ic1+1
           chgpos(1,ic1)=xb(1)-tu*xu(1)-tv*xv(1)
           chgpos(2,ic1)=xb(2)-tu*xu(2)-tv*xv(2)
           chgpos(3,ic1)=xb(3)-tu*xu(3)-tv*xv(3)
           atmcrg(1,ic1)=(chgpos(1,ic1)-cmid(1))*scale+rmid
           atmcrg(2,ic1)=(chgpos(2,ic1)-cmid(2))*scale+rmid
           atmcrg(3,ic1)=(chgpos(3,ic1)-cmid(3))*scale+rmid
           atmcrg(4,ic1)=fractcharge
           crgatn(ic1)=crgatnval
          end do
          end do
        endif


        end do
        return
        end
       
        subroutine basisortho(xa,xb,xu,xv,xw,modul)
c find a couple of versors orthogonal to (xa-xb),say xu and xv
c modul is the intensity of (xa-xb)

        real xb(3),xa(3),xu(3),xv(3),xw(3),tmpvect(3)
        real a,b,c,tmp,modul

        call diffvect(xa,xb,tmpvect)
        xu(3)=0
        if((abs(tmpvect(1)).lt.1.e-6).and.(abs(tmpvect(2)).lt.1.e-6))
     &  then
           xu(1)=1.0
           xu(2)=0.0

           xv(1)=0.0
           xv(2)=1.0
           xv(3)=0.0
           modul=abs(xb(3)-xa(3))
        else
           a=tmpvect(1)
           b=tmpvect(2)
           c=tmpvect(3)
           
           tmp=a*a+b*b
           xv(3)=-tmp
           modul=sqrt(tmp+c*c)
           tmp=1/sqrt(tmp)
           xu(1)=b*tmp
           xu(2)=-a*tmp
           tmp=tmp/modul
           xv(1)=a*c*tmp
           xv(2)=c*b*tmp
           xv(3)=xv(3)*tmp
        end if
        call mul(1/modul,tmpvect,xw)
        return
        end

        subroutine swap(xa,xb,moda,modb)
c swapping two vectors and their square modulus

        real xb(3),xa(3),tmpvect(3),moda,modb,tmp

        tmpvect(1)=xa(1)
        tmpvect(2)=xa(2)
        tmpvect(3)=xa(3)
        xa(1)=xb(1)
        xa(2)=xb(2)
        xa(3)=xb(3)
        xb(1)=tmpvect(1)
        xb(2)=tmpvect(2)
        xb(3)=tmpvect(3)
        tmp=moda
        moda=modb
        modb=tmp
           
        return
        end

