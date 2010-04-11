	subroutine cubedata(fac,cbln)
	include 'acc2.h'
	off=0.1
        xo=cmin(1)-fac*cbln-off
        yo=cmin(2)-fac*cbln-off
        zo=cmin(3)-fac*cbln-off
        xp=cmax(1)+fac*cbln+off
        yp=cmax(2)+fac*cbln+off
        zp=cmax(3)+fac*cbln+off
c       xo=-fac*cbln-off
c       yo=-fac*cbln-off
c       zo=-fac*cbln-off
c       xp=+fac*cbln+off
c       yp=+fac*cbln+off
c       zp=1.+fac*cbln+off

	bl1=xp-xo
	bl2=yp-yo
	bl3=zp-zo
	lcb=bl1/cbln
	mcb=bl2/cbln
	ncb=bl3/cbln
	cbai=1./cbln
	return
	end

	subroutine cube(natom,crd,rda,nobject,numbmol,scale,prbrd)
	include 'acc2.h'
	real crd(3,natom),rda(natom)
c here rda equals rad3
	integer cbn1(0:lcb,0:mcb,0:ncb),cbn2(0:lcb,0:mcb,0:ncb)
c b+++++++
        integer newatm,nobject,objecttype,itmp,numbmol
        integer cbal(1),kind 
c       integer cbal((natom+nobject-numbmol)*
c    &                max((lcb+1)*(mcb+1)*(ncb+1),27))
c  creating a set of fictious atoms occupying little cubes            
	integer icbn(3,natom+(nobject-numbmol)*(lcb+1)*(mcb+1)*(ncb+1))
c iatmobj connects the fictious atoms to the objects
        integer iatmobj((nobject-numbmol)*(lcb+1)*(mcb+1)*(ncb+1))
        character*80 dataobject(nobject,2)
        character*80 strtmp,strtmp1
        real vectx(3),vecty(3),vectz(3),modx,mody,dx,dy,dz,zeta,axdist
        real tmpvect(3),tmp,tmp1,limobject(nobject,3,2),dist,shift,scale
        real xa(3),xb(3),radius,modul,x2,y2,z2,tmpvect1(3),mod2,tmp2
        real tmpvect2(3),xc(3),xd(3),xq(3),alpha,tan2,dot,xloc(3),prbrd
        real cost
	i_icbn= memalloc(i_icbn,4*3*(natom+(nobject-numbmol)*(lcb+1)*
     &  (mcb+1)*(ncb+1)))
        i_iatmobj=memalloc(i_iatmobj,4*(nobject-numbmol)*(lcb+1)*
     &  (mcb+1)*(ncb+1))
        cbln=1./cbai
c e+++++++

	do i=0,lcb
	do j=0,mcb
	do k=0,ncb
          cbn1(i,j,k)=1
          cbn2(i,j,k)=0
c no longer needed, calloc superseded malloc
        end do
	end do
	end do

	do i=1,natom
        if(rda(i).gt.0.0)then
	x=(crd(1,i)-xo)*cbai
	ix=int(x)
	y=(crd(2,i)-yo)*cbai
	iy=int(y)
	z=(crd(3,i)-zo)*cbai
	iz=int(z)
        if(ix.lt.1.or.iy.lt.1.or.iz.lt.1)write(6,*)'ix,iy,iz: ',ix,iy,iz
        if(ix.ge.lcb.or.iy.ge.mcb.or.iz.ge.ncb)write(6,*)'ix,iy,iz: ',ix
     &  ,iy,iz
	do jz=iz-1,iz+1
	 do jy=iy-1,iy+1
	  do jx=ix-1,ix+1
	   cbn2(jx,jy,jz)=cbn2(jx,jy,jz)+1
	  end do
	 end do
	end do
        icbn(1,i)=ix
        icbn(2,i)=iy
        icbn(3,i)=iz
	endif
	end do
c b+++++++
        newatm=natom
        shift=0.5*cbln+0.55/scale+prbrd
        cost=cbln*.86602+.5/scale
c icbn will contain also coord center of fictious atoms
        do ii=1,nobject
          strtmp=dataobject(ii,1)
          read(strtmp(16:18),*)kind
          if (strtmp(1:4).ne.'is a'.and.kind.ne.2) then
            itmp=ii+natom
            do iz=0,ncb
              do iy=0,mcb
                do ix=0,lcb
                  xq(1)=(ix+0.5)*cbln+xo
                  xq(2)=(iy+0.5)*cbln+yo
                  xq(3)=(iz+0.5)*cbln+zo
                  if(limobject(ii,1,1).le.xq(1)+shift.and.
     &               limobject(ii,1,2).ge.xq(1)-shift.and.
     &               limobject(ii,2,1).le.xq(2)+shift.and.
     &               limobject(ii,2,2).ge.xq(2)-shift.and.
     &               limobject(ii,3,1).le.xq(3)+shift.and.
     &               limobject(ii,3,2).ge.xq(3)-shift )then

                     call distobj(xq,dx,dy,dz,nobject,ii,prbrd,dist
     &  ,.true.,zeta,axdist)
                    if (dist.le.cost) then
                      newatm=newatm+1
                      cbn2(ix,iy,iz)=cbn2(ix,iy,iz)+1
                      icbn(1,newatm)=ix
                      icbn(2,newatm)=iy
                      icbn(3,newatm)=iz
                      iatmobj(newatm-natom)=itmp
                    end if
                  end if
                end do
              end do
            end do
          end if
        end do
c e++++++++++
	icum=1
	do iz=0,ncb
	 do iy=0,mcb
	  do ix=0,lcb
	   if(cbn2(ix,iy,iz).gt.0)then
	   cbn1(ix,iy,iz)=icum
	   icum=icum+cbn2(ix,iy,iz)
	   endif
	  end do
	 end do
	end do

	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	endif
	end do
c b++++++++++++++++
        do i=natom+1,newatm
        ix=icbn(1,i)
        iy=icbn(2,i)
        iz=icbn(3,i)
        cbal(cbn1(ix,iy,iz))=iatmobj(i-natom)
        cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
        end do
c e++++++++++++++++
c -1,0,0
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix-1
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c       icbn(2,i)=iy
c       icbn(3,i)=iz
	endif
	end do

c 1,0,0
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix+2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do

c 0,-1,0
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix-1
	iy=iy-1
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do

c 0,1,0
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	iy=iy+2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
c      	icbn(1,i)=ix
	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do

c 0,0,-1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	iy=iy-1
	iz=iz-1
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
c      	icbn(1,i)=ix
	icbn(2,i)=iy
	icbn(3,i)=iz
	endif
	end do

c 0,0,1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	iz=iz+2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
c      	icbn(1,i)=ix
c      	icbn(2,i)=iy
	icbn(3,i)=iz
	endif
	end do
c nn=2
c 1,0,1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix+1
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do

c -1,0,1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix-2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c 0,1,1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix+1
	iy=iy+1
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c 0,-1,1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	iy=iy-2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
c      	icbn(1,i)=ix
	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c -1,-1,0
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix-1
	iz=iz-1
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
	icbn(3,i)=iz
	endif
	end do
c 1,-1,0
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix+2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c 1,1,0
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	iy=iy+2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
c      	icbn(1,i)=ix
	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c -1,1,0
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix-2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c -1,0,-1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	iz=iz-1
	iy=iy-1
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
c      	icbn(1,i)=ix
	icbn(2,i)=iy
	icbn(3,i)=iz
	endif
	end do
c 1,0,-1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix+2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c 0,1,-1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix-1
	iy=iy+1
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c 0,-1,-1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	iy=iy-2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
c      	icbn(1,i)=ix
	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c nn=3
c -1,-1,-1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix-1
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c 1,-1,-1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix+2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c 1,1,-1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	iy=iy+2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
c      	icbn(1,i)=ix
	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c -1,1,-1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix-2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c -1,1,1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	iz=iz+2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
c      	icbn(1,i)=ix
c      	icbn(2,i)=iy
	icbn(3,i)=iz
	endif
	end do
c 1,1,1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix+2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c 1,-1,1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	iy=iy-2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
c      	icbn(1,i)=ix
	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c -1,-1,1
	do i=1,natom
        if(rda(i).gt.0.0)then
	ix=icbn(1,i)
	iy=icbn(2,i)
	iz=icbn(3,i)
	ix=ix-2
	cbal(cbn1(ix,iy,iz))=i
	cbn1(ix,iy,iz)=cbn1(ix,iy,iz)+1
	icbn(1,i)=ix
c      	icbn(2,i)=iy
c      	icbn(3,i)=iz
	endif
	end do
c reset cbn1
	icum=1
	do iz=0,ncb
	 do iy=0,mcb
	  do ix=0,lcb
	   if(cbn2(ix,iy,iz).gt.0)then
	   cbn1(ix,iy,iz)=icum
	   icum=icum+cbn2(ix,iy,iz)
	   cbn2(ix,iy,iz)=icum-1
	   endif
	  end do
	 end do
	end do
	icum=icum-1
	i_icbn= memalloc(i_icbn,0)
c b++++++++++++++++
        i_iatmobj=memalloc(i_iatmobj,0)
c e+++++++++++++++

      return
      end
