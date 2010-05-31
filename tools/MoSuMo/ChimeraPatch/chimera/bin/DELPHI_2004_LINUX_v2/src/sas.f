c program to create the accessible surface arcs
c (S. Sridharan         Aug 1994, W. Rocchia Dec. 1999)

	subroutine sas(crd,natom,radprb,nacc,nobject,numbmol,scale)
	include 'acc2.h'
c	parameter(mxpr=250000)
	parameter(pi = 3.14159265)
	parameter(nver=520,nedge=1040)
        integer cbn1(1),cbn2(1),cbal(1)
	real crd(3,natom)
	integer edgv(2,nedge),edg(nedge),oti(nver),st(nedge)
	real ver(3,nver),rm(9)
c b++++++++++++++++++++++++++++++++++++++
c a third field in pls takes into account the correspondence nprobj-npr
        integer*4 pls(3,1)
        integer nobject,objecttype,itmp,jprec,kk,nprtobj,nprobj,inter
        integer numbmol,ii,jj,nside,dim,dim1,kind
        character*80 dataobject(nobject,2)
        character*80 strtmp,strtmp1
        real limobject(nobject,3,2),omin(3),omax(3),side,dist
        real vectx(3),tmp,tmp1,rad3(natom),xmin(3),xmax(3)
        real xa(3),xb(3),radius,modul,x2,y2,z2,vectz(3),mod2
        real vecty(3),xc(3),xd(3),xq(3),alpha,dot,radpmax,radprb(2)
        real coi(1,5),dx,dy,dz,zeta,seno,cose,modx,mody,modul2
        real tmp3,rad2
c coi contains circle of intersection data for pairs when
c objects are involved
c 1,2,3 = vector applied in the center of the sphere and pointing 
c to the center of the coi
c 4 => coi radius
c 5 => number of the intersections between an atom and an object
c e+++++++++++++++++++++++++++++++++++++++++++

	nacct=0
	nprt=0
        nprtobj=0
	nlvl=5
	nvi=12
c b++++++++++++++++++++++++++++
        radpmax=max(radprb(1),radprb(2))
        write(6,*)'radpmax,radprb ',radpmax,radprb(1),radprb(2)
c e+++++++++++++++++++++++++++
	cbln=2.*(rdmx+radpmax)
	call cubedata(1.0,cbln)
        dim=(lcb+1)*(mcb+1)*(ncb+1)
        i_cbn1= memalloc(i_cbn1,4*dim)
        i_cbn2= memalloc(i_cbn2,4*dim)
c b++++June2001+++++++++++++++++++++++
        dim1=27
        if ((nobject-numbmol).gt.0) dim1=max(dim,27)
c e+++++++++++++++++++++++++++++++++
        i_cbal= memalloc(i_cbal,4*dim1*(natom+nobject-numbmol))
	call cube(natom,crd,rad3,nobject,numbmol,scale,radprb(1))
c generate a template of vertices....
	tta=2.*pi/float(nvi)
	do i=1,nvi
	rdn=(i-1)*tta
	ver(1,i)=cos(rdn)
	ver(2,i)=sin(rdn)
	ver(3,i)=0.0
	j=i+1
	if(i.eq.nvi)j=1
	edgv(1,i)=i
	edgv(2,i)=j
	end do
	nv=nvi
	ne=nvi
	ie1=1
	ie2=0

	do ilvl=1,nlvl
	ie1=ie2+1
	ie2=ne
	do ie=ie1,ie2
	iv1=edgv(1,ie)
	iv2=edgv(2,ie)
	xm=ver(1,iv1)+ver(1,iv2)
	ym=ver(2,iv1)+ver(2,iv2)
	vmg=sqrt(xm*xm+ym*ym)
	nv=nv+1
	ver(1,nv)=xm/vmg
	ver(2,nv)=ym/vmg
	ver(3,nv)=0.0
	ne=ne+1
	edg(ie)=ne
	edgv(1,ne)=iv1
	edgv(2,ne)=nv
	ne=ne+1
	edgv(1,ne)=nv
	edgv(2,ne)=iv2
	end do
	end do
	ne=ie2
	do ie=ie1,ne
	edg(ie)=-1
	end do
	write(6,*)'# of vertices = ',nv,' # of edges = ',ne

	do i=1,natom
	  ast(i)=1
	end do

	nacc=0
	npr=0
        nprobj=0
	nprp=0
c it finds pairs.......
	do 70 i=1,natom
	rad=r0(i)
        rad2=r02(i)
	if(rad3(i).eq.0.)goto 70
	x1=crd(1,i)
	x2=crd(2,i)
	x3=crd(3,i)
	ix1=(x1-xo)*cbai
	ix2=(x2-yo)*cbai
	ix3=(x3-zo)*cbai
        liml=cbn1(ix1+1+(lcb+1)*ix2+(lcb+1)*(mcb+1)*ix3)
        limu=cbn2(ix1+1+(lcb+1)*ix2+(lcb+1)*(mcb+1)*ix3)

        if((npr+limu-liml+1).gt.nprt)then
          nprt=nprt+5000
          i_pls= memalloc(i_pls,4*3*nprt)
        endif

c b++++++++++++++++
        if((nprobj+limu-liml+1).gt.nprtobj)then
          nprtobj=nprtobj+1000
          i_coi= memalloc(i_coi,4*nprtobj*5)
        endif
c e++++++++++++++++

        jprec=0
	do jj=liml,limu
        j=cbal(jj)
        if (j.le.natom) then
	  radj=r0(j)
	  if(rad3(j).gt.0..and.j.gt.i)then
	    ctf=rad+radj
	    ctf2=ctf*ctf
	    dctf=abs(rad-radj)
	    dctf2=dctf*dctf
	    dx1=crd(1,j)-x1
	    dx2=crd(2,j)-x2
	    dx3=crd(3,j)-x3
	    d2=dx1*dx1+dx2*dx2+dx3*dx3
            del=ctf2-d2
	    if(del.gt.0.01.and.d2.gt.dctf2)then
	      npr=npr+1
	      pls(1,npr)=i
	      pls(2,npr)=j
	    endif
	  endif
        else
c b+++++++++++++++++++++
        if (j.ne.jprec) then
c it finds out if there is intersection between i and kk
c and it generates suitable parameters 
c kk= objectnumber
         kk=j-natom 
         strtmp=dataobject(kk,1)
         strtmp1=dataobject(kk,2)
         inter=0
         xq(1)=crd(1,i)
         xq(2)=crd(2,i)
         xq(3)=crd(3,i)
         read(strtmp(8:10),'(I3)')objecttype
         if (objecttype.eq.1) then
c          dealing with a sphere
           call distobj(xq,dx,dy,dz,nobject,kk,radprb(1),dist,.false.,
     &  zeta,axdist)
           if (abs(dist).lt.r0(i)) then
             inter=inter+1
             npr=npr+1
             nprobj=nprobj+1
             pls(1,npr)=i
             pls(2,npr)=j
             pls(3,npr)=nprobj
             coi(nprobj,1)=-dist*dx
             coi(nprobj,2)=-dist*dy
             coi(nprobj,3)=-dist*dz
             coi(nprobj,4)=sqrt(r02(i)-dist**2)
             coi(nprobj,5)=inter
           end if
         end if
         if (objecttype.eq.2) then
c          dealing with a cylinder
           call distobj(xq,dx,dy,dz,nobject,kk,radprb(1),dist,.true.,
     &  zeta,axdist)
           if (abs(dist).lt.r0(i)) then
             read(strtmp(20:80),*)xa,xb,radius
             read(strtmp1,'(5f8.3)')vectz,modul,modul2
             tmp=zeta+radprb(1)
             if(abs(tmp).lt.r0(i))then
c side B
               inter=inter+1
               npr=npr+1
               nprobj=nprobj+1
               pls(1,npr)=i
               pls(2,npr)=j
               pls(3,npr)=nprobj
               coi(nprobj,4)=sqrt(r02(i)-tmp**2)
               tmp=tmp/modul
               coi(nprobj,1)=vectz(1)*tmp
               coi(nprobj,2)=vectz(2)*tmp
               coi(nprobj,3)=vectz(3)*tmp
               coi(nprobj,5)=inter
             end if
             tmp=zeta-radprb(1)
             if(abs(tmp).lt.r0(i))then
c side A
               inter=inter+1
               npr=npr+1
               nprobj=nprobj+1
               pls(1,npr)=i
               pls(2,npr)=j
               pls(3,npr)=nprobj
               coi(nprobj,4)=sqrt(r02(i)-tmp**2)
               tmp=tmp/modul
               coi(nprobj,1)=vectz(1)*tmp
               coi(nprobj,2)=vectz(2)*tmp
               coi(nprobj,3)=vectz(3)*tmp
               coi(nprobj,5)=inter
             end if
             tmp=axdist-radius-radprb(1)
             if(abs(tmp).lt.r0(i))then
c lateral,closest, approximating with planes
               if(axdist.eq.0.)then
                 write(6,*)'cannot use planar approximation',i,j
                 go to 700
               end if
               inter=inter+1
               npr=npr+1
               nprobj=nprobj+1
               pls(1,npr)=i
               pls(2,npr)=j
               pls(3,npr)=nprobj
               coi(nprobj,4)=sqrt(r02(i)-tmp**2)
               tmp=tmp/axdist
               coi(nprobj,1)=tmp*(xq(1)-xb(1)-zeta*vectz(1)/modul)
               coi(nprobj,2)=tmp*(xq(2)-xb(2)-zeta*vectz(2)/modul)
               coi(nprobj,3)=tmp*(xq(3)-xb(3)-zeta*vectz(3)/modul)
               coi(nprobj,5)=inter
700            continue
             end if
             tmp=axdist+radius+radprb(1)
             if(abs(tmp).lt.r0(i))then
c lateral,farthest, approximating with planes
               write(6,*)'planar approx very poor, sphere too big',i,j
               if(axdist.eq.0.)then
                 write(6,*)'cannot use planar approximation',i,j
                 go to 710
               end if
               inter=inter+1
               npr=npr+1
               nprobj=nprobj+1
               pls(1,npr)=i
               pls(2,npr)=j
               pls(3,npr)=nprobj
               coi(nprobj,4)=sqrt(r02(i)-tmp**2)
               tmp=tmp/axdist
               coi(nprobj,1)=tmp*(xq(1)-xb(1)-zeta*vectz(1)/modul)
               coi(nprobj,2)=tmp*(xq(2)-xb(2)-zeta*vectz(2)/modul)
               coi(nprobj,3)=tmp*(xq(3)-xb(3)-zeta*vectz(3)/modul)
               coi(nprobj,5)=inter
710            continue
             end if
           end if
         end if

         if (objecttype.eq.3) then
c          dealing with a cone
           call distobj(xq,dx,dy,dz,nobject,kk,radprb(1),dist,.true.,
     &  zeta,axdist)
           if (abs(dist).lt.r0(i)) then
             read(strtmp(20:80),*)xa,xb,alpha
             alpha=alpha*3.1415/180
             seno=sin(alpha)
             cose=cos(alpha)
             read(strtmp1,'(5f8.3)')vectz,modul,modul2

             tmp=zeta+radprb(1)
             if(abs(tmp).lt.r0(i))then
c side B
               inter=inter+1
               npr=npr+1
               nprobj=nprobj+1
               pls(1,npr)=i
               pls(2,npr)=j
               pls(3,npr)=nprobj
               coi(nprobj,4)=sqrt(r02(i)-tmp**2)
               tmp=tmp/modul
               coi(nprobj,1)=vectz(1)*tmp
               coi(nprobj,2)=vectz(2)*tmp
               coi(nprobj,3)=vectz(3)*tmp
               coi(nprobj,5)=inter
             end if
             tmp=axdist*cose-radprb(1)-seno*(modul-zeta)
             if(abs(tmp).lt.r0(i))then
c lateral,closest, approximating with planes
               if(axdist.eq.0.)then
                 write(6,*)'no planar approx since sphere too large',i,j
                 go to 800
               end if
               inter=inter+1
               npr=npr+1
               nprobj=nprobj+1
               pls(1,npr)=i
               pls(2,npr)=j
               pls(3,npr)=nprobj
               coi(nprobj,4)=sqrt(r02(i)-tmp**2)
               tmp=tmp*cose/axdist
               coi(nprobj,1)=tmp*(xb(1)-xq(1)+(zeta-axdist*seno/cose)*
     &  vectz(1)/modul)
               coi(nprobj,2)=tmp*(xb(2)-xq(2)+(zeta-axdist*seno/cose)*
     &  vectz(2)/modul)
               coi(nprobj,3)=tmp*(xb(3)-xq(3)+(zeta-axdist*seno/cose)*
     &  vectz(3)/modul)
               coi(nprobj,5)=inter
800            continue
             end if
             tmp=seno*(modul-zeta)+cose*axdist+radprb(1)
             if(tmp.lt.r0(i))then
               if(zeta.gt.modul+radprb(1).or.axdist.eq.0.) then
                 write(6,*)'cannot use planar approx in this pos',i,j
                 go to 810
               endif
c lateral,farthest, approximating with planes
               inter=inter+1
               npr=npr+1
               nprobj=nprobj+1
               pls(1,npr)=i
               pls(2,npr)=j
               pls(3,npr)=nprobj
               coi(nprobj,4)=sqrt(r02(i)-tmp**2)
               tmp=tmp/axdist
               coi(nprobj,1)=tmp*(-cose*(xq(1)-xb(1))+(cose*zeta+axdist
     &  *seno)*vectz(1)/modul)
               coi(nprobj,2)=tmp*(-cose*(xq(2)-xb(2))+(cose*zeta+axdist
     &  *seno)*vectz(2)/modul)
               coi(nprobj,3)=tmp*(-cose*(xq(3)-xb(3))+(cose*zeta+axdist
     &  *seno)*vectz(3)/modul)
               coi(nprobj,5)=inter
810            continue
             end if
             if(zeta.gt.modul+radprb(1).and.axdist.lt.1.0e-6) then
c beyond the tip, close to the axis
               inter=inter+1
               npr=npr+1
               nprobj=nprobj+1
               pls(1,npr)=i
               pls(2,npr)=j
               pls(3,npr)=nprobj
               tmp=(dist-r0(i))*(1.-cose)/modul
               coi(nprobj,4)=r0(i)*seno
               coi(nprobj,1)=tmp*vectz(1)
               coi(nprobj,2)=tmp*vectz(2)
               coi(nprobj,3)=tmp*vectz(3)
               coi(nprobj,5)=inter
             endif
           end if
         end if

         if (objecttype.eq.4) then
c          dealing with a parallelepiped
           read(strtmp(20:80),*)xa,xb,xc,xd
           read(strtmp1,'(12f6.2)')vectz,modul,vecty,mody,vectx,modx
c          now using the newest notation for box vertices
c          new notation:vectx=B-A,vecty=C-A,vectz=D-A;xq=P-A;
c chiamate da togliere!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
           xq(1)=xq(1)-xa(1)
           xq(2)=xq(2)-xa(2)
           xq(3)=xq(3)-xa(3)
c working on z interval
           dot=vectz(1)*xq(1)+vectz(2)*xq(2)+vectz(3)*xq(3)
           tmp=dot/modul
           tmp1=radprb(1)+modul
           if (tmp.gt.-radprb(1)-rad.and.tmp.lt.rad+tmp1) then
             tmp2=tmp1-tmp
             rdx2=rad2-tmp2**2
             tmp3=radprb(1)+tmp
             rsx2=rad2-tmp3**2
             if (rdx2.gt.0.0) then
                inter=inter+1
                npr=npr+1
                nprobj=nprobj+1
                pls(1,npr)=i
                pls(2,npr)=j
                pls(3,npr)=nprobj
                tmp2=tmp2/modul
                coi(nprobj,1)=vectz(1)*tmp2
                coi(nprobj,2)=vectz(2)*tmp2
                coi(nprobj,3)=vectz(3)*tmp2
                coi(nprobj,4)=sqrt(rdx2)
                coi(nprobj,5)=inter
             endif
             if (rsx2.gt.0.0) then
                inter=inter+1
                npr=npr+1
                nprobj=nprobj+1
                pls(1,npr)=i
                pls(2,npr)=j
                pls(3,npr)=nprobj
                tmp3=-tmp3/modul
                coi(nprobj,1)=vectz(1)*tmp3
                coi(nprobj,2)=vectz(2)*tmp3
                coi(nprobj,3)=vectz(3)*tmp3
                coi(nprobj,4)=sqrt(rsx2)
                coi(nprobj,5)=inter
             endif
c working on y interval
             dot=vecty(1)*xq(1)+vecty(2)*xq(2)+vecty(3)*xq(3)
             tmp=dot/mody
             tmp1=radprb(1)+mody
             tmp2=tmp1-tmp
             rdx2=rad2-tmp2**2
             tmp3=radprb(1)+tmp
             rsx2=rad2-tmp3**2
             if (rdx2.gt.0.0) then
                inter=inter+1
                npr=npr+1
                nprobj=nprobj+1
                pls(1,npr)=i
                pls(2,npr)=j
                pls(3,npr)=nprobj
                tmp2=tmp2/mody
                coi(nprobj,1)=vecty(1)*tmp2
                coi(nprobj,2)=vecty(2)*tmp2
                coi(nprobj,3)=vecty(3)*tmp2
                coi(nprobj,4)=sqrt(rdx2)
                coi(nprobj,5)=inter
             endif
             if (rsx2.gt.0.0) then
                inter=inter+1
                npr=npr+1
                nprobj=nprobj+1
                pls(1,npr)=i
                pls(2,npr)=j
                pls(3,npr)=nprobj
                tmp3=-tmp3/mody
                coi(nprobj,1)=vecty(1)*tmp3
                coi(nprobj,2)=vecty(2)*tmp3
                coi(nprobj,3)=vecty(3)*tmp3
                coi(nprobj,4)=sqrt(rsx2)
                coi(nprobj,5)=inter
             endif
c working on x interval
             dot=vectx(1)*xq(1)+vectx(2)*xq(2)+vectx(3)*xq(3)
             tmp=dot/modx
             tmp1=radprb(1)+modx
             tmp2=tmp1-tmp
             rdx2=rad2-tmp2**2
             tmp3=radprb(1)+tmp
             rsx2=rad2-tmp3**2
             if (rdx2.gt.0.0) then
                inter=inter+1
                npr=npr+1
                nprobj=nprobj+1
                pls(1,npr)=i
                pls(2,npr)=j
                pls(3,npr)=nprobj
                tmp2=tmp2/modx
                coi(nprobj,1)=vectx(1)*tmp2
                coi(nprobj,2)=vectx(2)*tmp2
                coi(nprobj,3)=vectx(3)*tmp2
                coi(nprobj,4)=sqrt(rdx2)
                coi(nprobj,5)=inter
             endif
             if (rsx2.gt.0.0) then
                inter=inter+1
                npr=npr+1
                nprobj=nprobj+1
                pls(1,npr)=i
                pls(2,npr)=j
                pls(3,npr)=nprobj
                tmp3=-tmp3/modx
                coi(nprobj,1)=vectx(1)*tmp3
                coi(nprobj,2)=vectx(2)*tmp3
                coi(nprobj,3)=vectx(3)*tmp3
                coi(nprobj,4)=sqrt(rsx2)
                coi(nprobj,5)=inter
             endif
           endif
         end if 
        end if
c end of j.le.natom
        endif
        jprec=j
c e++++++++++++++++++++
	end do
	if(npr.eq.nprp)then
	  ast(i)=0
	endif
	nprp=npr
70	continue
	write(6,*)'# of pairs = ',npr

	call ddtime(tary)
	write(6,*)'time to find all pairs = ',tary(1)

        cbln=rdmx+radpmax
	call cubedata(2.0,cbln)
        dim=(lcb+1)*(mcb+1)*(ncb+1)
        i_cbn1= memalloc(i_cbn1,4*dim)
        i_cbn2= memalloc(i_cbn2,4*dim)
c b++++June2001+++++++++++++++++++++++
        dim1=27
        if ((nobject-numbmol).gt.0) dim1=max(dim,27)
c e+++++++++++++++++++++++++++++++++
        i_cbal= memalloc(i_cbal,4*dim1*(natom+nobject-numbmol))

	call cube(natom,crd,rad3,nobject,numbmol,scale,radprb(1))
	nprx=0
	do ip=1,npr
	i=pls(1,ip)
	j=pls(2,ip)

        if (j.le.natom) then
          dx1=crd(1,j)-crd(1,i)
	  dx2=crd(2,j)-crd(2,i)
	  dx3=crd(3,j)-crd(3,i)
	  d2=dx1*dx1+dx2*dx2+dx3*dx3
	  dmg=sqrt(d2)
	  pre=1.+(r02(i)-r02(j))/d2
	  tij1=crd(1,i)+0.5*pre*dx1
	  tij2=crd(2,i)+0.5*pre*dx2
	  tij3=crd(3,i)+0.5*pre*dx3
	  rij=0.5*sqrt((r0(i)+r0(j))**2-d2)*
     &	sqrt(d2-(r0(i)-r0(j))**2)/dmg
        else
c b+++++++++++++++++++++++++++++++
          nprobj=pls(3,ip)
          rij=coi(nprobj,4)
c pay attention, here dx has a different meaning from previous one
          dx1=coi(nprobj,1)
          dx2=coi(nprobj,2)
          dx3=coi(nprobj,3)
          tij1=crd(1,i)+dx1
          tij2=crd(2,i)+dx2
          tij3=crd(3,i)+dx3
          d2=dx1*dx1+dx2*dx2+dx3*dx3
          dmg=sqrt(d2)
        endif
c e+++++++++++++++++++++++++++++++
        rvmg=sqrt(dx1*dx1+dx2*dx2)
	if(rvmg.gt.1.0e-8)then
	rv1=-dx2/rvmg
	rv2=dx1/rvmg
	cst=dx3/dmg
	snt=sqrt(1.-cst*cst)
c	snt=rvmg/dmg    !doesn't lead to any improved performance
	csp=1.0-cst
	tm=csp*rv1
	sm1=snt*rv1
	sm2=snt*rv2

	rm(1)=tm*rv1+cst
	rm(4)=tm*rv2
	rm(7)=sm2
	rm(2)=tm*rv2
	rm(5)=csp*rv2*rv2+cst
	rm(8)=-sm1
	rm(3)=-sm2
	rm(6)=sm1
	rm(9)=cst
	else
        rm(1)=1.0
        rm(4)=0.0
        rm(7)=0.0
        rm(2)=0.0
        rm(5)=1.0
        rm(8)=0.0
        rm(3)=0.0
        rm(6)=0.0
        rm(9)=1.0
	endif
	nvo=0
	nbv=0
c assign memory to expos if needed
        if((nacc+nv).gt.nacct)then
        nacct=nacct+1000
        i_expos= memalloc(i_expos,4*3*nacct)
        endif

	do 10 iv=1,nvi
c +rm(7)*ver(3,iv) has been removed because it is always zero
	cf1=rm(1)*ver(1,iv)+rm(4)*ver(2,iv)
	cf2=rm(2)*ver(1,iv)+rm(5)*ver(2,iv)
	cf3=rm(3)*ver(1,iv)+rm(6)*ver(2,iv)
	cf1=tij1+rij*cf1
	cf2=tij2+rij*cf2
	cf3=tij3+rij*cf3
c b+++++++++++++++++++++++++++++
        if (j.gt.natom) then
         inter=coi(nprobj,5)
         if (inter.gt.1) then
c if inter>1 we are close to tips in object, thus, false vertices might
c have been previously generated, so now, if a vertex is outside the 
c object it is fictiously checked for occlusion by oti but discarded
c afterwards
c kk= objectnumber
           kk=j-natom
           xq(1)=cf1
           xq(2)=cf2
           xq(3)=cf3
           call distobj(xq,dx,dy,dz,nobject,kk,radprb(1),dist,.true.,
     &  zeta,axdist)
           if (dist.gt.5.0e-4) then 
             oti(iv)=j
             goto 10
           end if
         endif
        endif
c e+++++++++++++++++++++++++++++

	ic1=(cf1-xo)*cbai
	ic2=(cf2-yo)*cbai
	ic3=(cf3-zo)*cbai
        liml=cbn1(ic1+1+(lcb+1)*ic2+(lcb+1)*(mcb+1)*ic3)
        limu=cbn2(ic1+1+(lcb+1)*ic2+(lcb+1)*(mcb+1)*ic3)
	do ii=liml,limu
	k=cbal(ii)
c b+++++++++++++++++++++
        if (k.gt.natom) then
           oti(iv)=k
           goto 5
        endif
c e+++++++++++++++++++++
	dy1=crd(1,k)-cf1
	dy2=crd(2,k)-cf2
	dy3=crd(3,k)-cf3
	ds2=dy1*dy1+dy2*dy2+dy3*dy3
	if(ds2.lt.rs2(k))then
	oti(iv)=k
	goto 10
	endif
5       continue
	end do
	nvo=nvo+1
	nacc=nacc+1
	expos(1,nacc)=cf1
	expos(2,nacc)=cf2
	expos(3,nacc)=cf3
	oti(iv)=0
10	continue

	nst=0
	if(nlvl.gt.0)then
	do 20 ie=nvi,1,-1
	ia1=oti(edgv(1,ie))
	ia2=oti(edgv(2,ie))
	if(ia1.gt.0.and.ia1.eq.ia2)goto 20
	nst=nst+1
	st(nst)=ie
20	continue
	endif
	
	if(nst.gt.0)then
30	ie=st(nst)
	nst=nst-1
	ia1=oti(edgv(1,ie))
	ia2=oti(edgv(2,ie))
c b++++++++++++++++++++++
        if ((ia1.gt.natom).or.(ia2.gt.natom)) goto 60
c e++++++++++++++++++++++
	iv=ie+nvi
c rm(7)*ver(3,iv) has been removed because it is always zero
	cf1=rm(1)*ver(1,iv)+rm(4)*ver(2,iv)
	cf2=rm(2)*ver(1,iv)+rm(5)*ver(2,iv)
	cf3=rm(3)*ver(1,iv)+rm(6)*ver(2,iv)
	cf1=tij1+rij*cf1
	cf2=tij2+rij*cf2
	cf3=tij3+rij*cf3

	if(ia1.eq.0)goto 40
	dy1=crd(1,ia1)-cf1
	dy2=crd(2,ia1)-cf2
	dy3=crd(3,ia1)-cf3
	ds2=dy1*dy1+dy2*dy2+dy3*dy3
c	 write(6,*)'ia1 = ',ia1,' dis = ',r0(ia1)-sqrt(ds2)
	if(ds2.lt.rs2(ia1))then
	oti(iv)=ia1
	if(edg(ie).gt.0)then
	nst=nst+1
	st(nst)=edg(ie)+1
	endif
	goto 60
	endif
40	continue
	if(ia2.eq.0)goto 50
	dy1=crd(1,ia2)-cf1
	dy2=crd(2,ia2)-cf2
	dy3=crd(3,ia2)-cf3
	ds2=dy1*dy1+dy2*dy2+dy3*dy3
c	 write(6,*)'ia2 = ',ia2,' dis = ',r0(ia2)-sqrt(ds2)
	if(ds2.lt.rs2(ia2))then
	oti(iv)=ia2
	if(edg(ie).gt.0)then
	nst=nst+1
	st(nst)=edg(ie)
	endif
	goto 60
	endif
50	continue
	ic1=(cf1-xo)*cbai
	ic2=(cf2-yo)*cbai
	ic3=(cf3-zo)*cbai
        liml=cbn1(ic1+1+(lcb+1)*ic2+(lcb+1)*(mcb+1)*ic3)
        limu=cbn2(ic1+1+(lcb+1)*ic2+(lcb+1)*(mcb+1)*ic3)
	do ii=liml,limu
	k=cbal(ii)
c b+++++++++++++++++++++
        if (k.gt.natom) then
           oti(iv)=k
           goto 55
        endif
c e+++++++++++++++++++++
	dy1=crd(1,k)-cf1
	dy2=crd(2,k)-cf2
	dy3=crd(3,k)-cf3
	ds2=dy1*dy1+dy2*dy2+dy3*dy3
	if(ds2.lt.rs2(k))then
c	 write(6,*)'k = ',k,' dis = ',r0(k)-sqrt(ds2)
	oti(iv)=k
	if(edg(ie).gt.0)then
	nst=nst+1
	st(nst)=edg(ie)+1
	nst=nst+1
	st(nst)=edg(ie)
	endif
	goto 60
	endif
55      continue
	end do
	nvo=nvo+1
	nacc=nacc+1
	expos(1,nacc)=cf1
	expos(2,nacc)=cf2
	expos(3,nacc)=cf3
	oti(iv)=0
	if(edg(ie).gt.0)then
	if(edg(edg(ie)+1).gt.0.or.ia2.gt.0)then
	nst=nst+1
	st(nst)=edg(ie)+1
	endif
	if(edg(edg(ie)).gt.0.or.ia1.gt.0)then
	nst=nst+1
	st(nst)=edg(ie)
	endif
	endif
60	if(nst.gt.0)goto 30
	endif

	if(nvo.gt.0)then
c b+++++++++++++++++++++++++
c considering pairs also where one 'partner' is an object
          nprx=nprx+1
          ast(i)=0
          if (j.le.natom) ast(j)=0
c e++++++++++++++++++++++++
	endif

	end do

	i_pls= memalloc(i_pls,0)
c b++++++++++++
        i_coi= memalloc(i_coi,0)
c e++++++++++++++
	i_cbn1= memalloc(i_cbn1,0)
	i_cbn2= memalloc(i_cbn2,0)
	i_cbal= memalloc(i_cbal,0)


	nxa=0
	do i=1,natom
	   if(ast(i).eq.0)nxa=nxa+1
	end do

c b+++++++++++++++++++++++++++++++++++++++++
        if (nobject-numbmol.gt.1) then
          write(6,*)'now calculating object-object exposed vertices'
          call ddtime(tary)
          jj=0
          do ii=1,nobject
            strtmp=dataobject(ii,1)
            read(strtmp(16:18),*)kind
            if (strtmp(1:4).ne.'is a'.and.kind.ne.2) then
              if (jj.eq.0) then
              do i=1,3
                omin(i)=limobject(ii,i,1)
                omax(i)=limobject(ii,i,2)
              end do
              end if
              jj=1
              do i=1,3
                omin(i)=min(omin(i),limobject(ii,i,1))
                omax(i)=max(omax(i),limobject(ii,i,2))
              end do
            end if
          end do
c make cubedata
c nside = number of initial subdivisions
          nside=4
c for objects, only water probes involved
          tmp=omax(1)-omin(1)+2*radprb(1)
          tmp=min(tmp,omax(2)-omin(2)+2*radprb(1))
          tmp=min(tmp,omax(3)-omin(3)+2*radprb(1))
80        continue
          side=tmp/float(nside)
          do i=1,3
            xmin(i)=omin(i)-radprb(1)+.5*side
            xmax(i)=omax(i)+radprb(1)-.5*side      
            xmax(i)=omin(i)+side*(0.5+int(0.999+(xmax(i)-xmin(i))/side))
          end do
          h=1./scale
          sideinter=amax1(amin1(0.25,h/4),0.05) 
          sidemin=sideinter/4
          write(6,*)'Generating vertices between objects:'
          write(6,*)'Finite difference step:',h
          write(6,*)'Initial side:',side
          write(6,*)'Intermediate side:',sideinter
          write(6,*)'Minimum side:',sidemin
          nacct=nacc+(side/sidemin)**3
          write(6,*)'threshold for number of exposed vertices:',nacct
          i_expos= memalloc(i_expos,4*3*nacct)
          call objvertices(nacc,nobject,xmin,xmax,side,h,natom,
     &  (numbmol.gt.0))
          write(6,*)'time = ',tary(1)
        end if
c e++++++++++++++++++++++++++++++++++++++++++

        write(6,*)'# pairs analyzed (atom-atom and atom-object)= ',npr
        write(6,*)'# exposed pairs (atom-atom and atom-object)= ',nprx
        write(6,*)'no. arc points  = ',nacc
        write(6,*)'no. surface atoms  = ',nxa,' nbur = ',natom-nxa
c	if(nacc.gt.exmax)stop 'nacc limit exceeded'

	end
