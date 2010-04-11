c program to reposition the boundary grid points on the molecular surface
c (S. Sridharan         May 1994)
	subroutine sclbp(natom,igrid,xn1,scale,radprb,oldmid,ibnum,
     &	extot,iall,vcrd,vnr,nobject,numbmol,ibnumsurf)
	include 'acc2.h'
        integer iab1(0:lcb1,0:mcb1,0:ncb1),iab2(0:lcb1,0:mcb1,0:ncb1)
     &	,icume(1)
        integer cbn1(1),cbn2(1),cbal(1)
	integer nbra(1000)
	integer atndx(1)
	real xn1(3,natom),rad3(natom),oldmid(3),vnr(3,ibnum)
	real vcrd(3,ibnum),dis,dist
	logical out,outcb(-2:2,-2:2,-2:2)
c b+++++++++++++++++++++++++++++++++++++++++
        integer iaprec,nobject,objecttype,nearest,even,dim1,kind
        integer numbmol,dim,prevmed,med,iatmmed(natom+nobject)
        integer ibnumsurf,epsdim,imezzo(6),iente(6),ix,iy,iz
        integer iepsmp(igrid,igrid,igrid,3),atsurf(ibnum)
        logical*1 internal(nobject)
        logical lga,lgd,iflag,precedenza,vicinanza
        character*80 dataobject(nobject,2)
        character*80 strtmp
        real limobject(nobject,3,2),disev,disodd,radprb(2)
        real vectx(3),tmp(6),vnor(3),radpmax,dst,zeta
        real radius,modul(3),vectz(3),mod2(3),axdist
        real vecty(3),xq(3),alpha,tan2,dot(3),dx,dy,dz
        real dix,diy,diz,hgs
        i_internal=memalloc(i_internal,-nobject)
        epsdim=natom+nobject+2
        iflag=.false.
c e++++++++++++++++++++++++++++++++++++++++
	i_atsurf= memalloc(i_atsurf,4*ibnum)
	i_atndx= memalloc(i_atndx,4*ibnum)
        iall=0
c hgs= half grid spacing
        hgs=1./(2.*scale)
	do i=-2,2
	do j=-2,2
	do k=-2,2
	  outcb(i,j,k)=.true.
	end do
	end do
	end do
	do i=-1,1
	do j=-1,1
	do k=-1,1
	  outcb(i,j,k)=.false.
	end do
	end do
	end do
c convertion from grid to real coordinates(can also use routine gtoc)
	x1=1.0/scale
	x1x=oldmid(1)-x1*float(igrid+1)*0.5
	x1y=oldmid(2)-x1*float(igrid+1)*0.5
	x1z=oldmid(3)-x1*float(igrid+1)*0.5
        radpmax=max(radprb(1),radprb(2))
	if(extot.eq.0.and.radpmax.gt.0.0.and.(nobject.gt.1.or.natom.
     &  gt.1))then
c find extrema
c b++++++++++++++++++++
c ++++++++++++here one should consider the global system (Walter)
          write(6,*)'Scaling routine in action!'
	  cmin(1)=6000
	  cmin(2)=6000
	  cmin(3)=6000
	  cmax(1)=-6000
	  cmax(2)=-6000
	  cmax(3)=-6000
          do ii=1,nobject
            cmin(1)=min(cmin(1),limobject(ii,1,1))
            cmin(2)=min(cmin(2),limobject(ii,2,1))
            cmin(3)=min(cmin(3),limobject(ii,3,1))
            cmax(1)=max(cmax(1),limobject(ii,1,2))
            cmax(2)=max(cmax(2),limobject(ii,2,2))
            cmax(3)=max(cmax(3),limobject(ii,3,2))
          end do
c       rdmx=0.0
c       do 2103 ix=1,natom
c       cmin(1)=min(cmin(1),xn1(1,ix))
c       cmin(2)=min(cmin(2),xn1(2,ix))
c       cmin(3)=min(cmin(3),xn1(3,ix))
c       cmax(1)=max(cmax(1),xn1(1,ix))
c       cmax(2)=max(cmax(2),xn1(2,ix))
c       cmax(3)=max(cmax(3),xn1(3,ix))
c       rdmx=max(rdmx,rad3(ix))
c2103    continue

	  call sas(xn1,natom,radprb,extot,nobject,numbmol,scale)
	endif

	del=radpmax
	del=max(del,1./(2.*scale))
        cbln=rdmx+del
	call cubedata(2.0,cbln)
        dim=(lcb+1)*(mcb+1)*(ncb+1)
        i_cbn1= memalloc(i_cbn1,4*dim)
        i_cbn2= memalloc(i_cbn2,4*dim)
c b++++June2001+++++++++++++++++++++++
        dim1=27
        if ((nobject-numbmol).gt.0) dim1=max(dim,27)
c e+++++++++++++++++++++++++++++++++
        i_cbal= memalloc(i_cbal,4*dim1*(natom+nobject-numbmol))

	call cube(natom,xn1,rad3,nobject,numbmol,scale,radprb(1))

	ncbp=0
	do i=1,ibnum
c b+++++++++per trattare molecole con diversa epsilon++01/2002+
          if(ibnum.ne.ibnumsurf.and.numbmol.gt.1) then
            ix=vcrd(1,i)
            iy=vcrd(2,i)
            iz=vcrd(3,i)
            iflag=.false.
            iente(1)=mod(iepsmp(ix,iy,iz,1),epsdim)
            iente(2)=mod(iepsmp(ix,iy,iz,2),epsdim)
            iente(3)=mod(iepsmp(ix,iy,iz,3),epsdim)
            iente(4)=mod(iepsmp(ix-1,iy,iz,1),epsdim)
            iente(5)=mod(iepsmp(ix,iy-1,iz,2),epsdim)
            iente(6)=mod(iepsmp(ix,iy,iz-1,3),epsdim)
            imezzo(1)=iepsmp(ix,iy,iz,1)/epsdim
            imezzo(2)=iepsmp(ix,iy,iz,2)/epsdim
            imezzo(3)=iepsmp(ix,iy,iz,3)/epsdim
            imezzo(4)=iepsmp(ix-1,iy,iz,1)/epsdim
            imezzo(5)=iepsmp(ix,iy-1,iz,2)/epsdim
            imezzo(6)=iepsmp(ix,iy,iz-1,3)/epsdim
c guardo se ho due molecole con diversa epsilon nel punto,interno
            if(imezzo(1).ne.imezzo(6).and.imezzo(1)*imezzo(6).ne.0) 
     &           iflag=(iente(1).le.natom+1.and.iente(6).le.natom+1)
            do ii=2,6
              if(imezzo(ii).ne.imezzo(ii-1).and.imezzo(ii)*imezzo(ii-1)
     &.ne.0) iflag=iflag.or.(iente(ii).le.natom+1.and.iente(ii-1).le.
     &natom+1)
            end do
          end if
c iflag vale 1 se devo trascurare lo shift del bgp
c e++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
          xg1=vcrd(1,i)*x1+x1x
          xg2=vcrd(2,i)*x1+x1y
          xg3=vcrd(3,i)*x1+x1z
c find the closest surface atom to the gridpoint
	  it1=(xg1-xo)*cbai
	  it2=(xg2-yo)*cbai
	  it3=(xg3-zo)*cbai
          dmn=100.
          prevmed=0
          iac=0
          nnbr=0
c b++++++++++++++++++++++++++++++++++++++
          if(it1.lt.0.or.it1.gt.lcb.or.it2.lt.0.or.it2.gt.mcb.or.it3.lt.
     &  0.or.it3.gt.ncb) then
c if the bgp is outside the cube, probably it is due to some object
            do ii=1,nobject
              strtmp=dataobject(ii,1)
              read(strtmp(16:18),*)kind
              if (strtmp(1:4).ne.'is a'.and.kind.ne.2) then
                if ((xg1.le.limobject(ii,1,2)+x1).and.(xg1.gt.
     &                                  limobject(ii,1,1)-x1))then
                if ((xg2.le.limobject(ii,2,2)+x1).and.(xg2.gt.
     &                                  limobject(ii,2,1)-x1))then
                if ((xg3.le.limobject(ii,3,2)+x1).and.(xg3.gt.
     &                                  limobject(ii,3,1)-x1))then
                  nnbr=nnbr+1
                  nbra(nnbr)=ii+natom
                  liml=1
                  limu=0
                endif
                endif
                endif 
              endif
            end do
            if(liml.ne.1.or.limu.ne.0) write(6,*)'bgp close to nothing'
          else 
c e+++++++++++++++++++++++++++++++++++++++++
            liml=cbn1(it1+1+(lcb+1)*it2+(lcb+1)*(mcb+1)*it3)
            limu=cbn2(it1+1+(lcb+1)*it2+(lcb+1)*(mcb+1)*it3)
          endif

          iaprec=0
	  do kk=liml,limu
	    ia=cbal(kk)
            if (ia.le.natom) then
c b+aggiunto iflag per salvare comunque in atsurf valore del + vicino (01/02)
c non sono sicurissimo perche' non ricordo esattmente che fa poi con prevmed...
	      if(ast(ia).eq.0.or.iflag)then
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  	        nnbr=nnbr+1
  	        nbra(nnbr)=ia
              endif
            else
c b+++++++++++++++++++++++++++++++++
              if (ia.ne.iaprec)then
                iaprec=ia
                nnbr=nnbr+1
                nbra(nnbr)=ia
              endif
c e++++++++++++++++++++++++++++++++
            endif
	  end do
	  do ii=1,nnbr
	    ia=nbra(ii)
c b+++++++++++++++++++++++++++++++
            med=iatmmed(ia)
            lgd=(med.ne.prevmed)
            if (ia.gt.natom) then
              iii=ia-natom 
              xq(1)=xg1
              xq(2)=xg2
              xq(3)=xg3
c try to find closest VdW surface, better if it is buried
c internal is used for the object to which surface the bgp is closer
              call distobj(xq,dix,diy,diz,nobject,iii,0.0,dist,.false.
     &  ,zeta,axdist)
              precedenza=ia.gt.iac.and.(iac.gt.natom.or.iac.eq.0)
              vicinanza=abs(dist).lt.abs(dmn) 
              lga=(precedenza.and.(vicinanza.or.dist.lt.0.)).or.
     &            (vicinanza.and.dmn.gt.0.)
              if((dist.lt.dmn.and..not.lgd).or.(lga.and.lgd))then
                dmn=dist
                iac=ia
                prevmed=med
                dr1=dix*(dist-radprb(1))
                dr2=diy*(dist-radprb(1))
                dr3=diz*(dist-radprb(1))
                vnor(1)=dix
                vnor(2)=diy
                vnor(3)=diz
              end if
              internal(iii)=(dist.lt.0.0)
            else
c e++++++++++++++++++++++++++++++
	      dx1=xg1-xn1(1,ia)
	      dx2=xg2-xn1(2,ia)
	      dx3=xg3-xn1(3,ia)
	      ds2=dx1*dx1+dx2*dx2+dx3*dx3
	      dis=sqrt(ds2)-rad3(ia)
c b++++++++++++++++++++++++++++++
              precedenza=ia.gt.iac.or.iac.gt.natom
              vicinanza=abs(dis).lt.abs(dmn)
              lga=(precedenza.and.(vicinanza.or.dis.lt.0.)).or.
     &           (vicinanza.and.dmn.gt.0.)
              if((dis.lt.dmn.and..not.lgd).or.(lga.and.lgd))then
                prevmed=med
c e++++++++++++++++++++++++++++++
	        dmn=dis
	        iac=ia
	      endif
            endif
	  end do
	  atsurf(i)=iac
c b++++per mol. con diversa eps+++++++++++++01/02++++++++++++++
          if (iflag) then
            atndx(i)=-1
            vcrd(1,i)=xg1
            vcrd(2,i)=xg2
            vcrd(3,i)=xg3
            vnr(1,i)=0.0
            vnr(2,i)=0.0
            vnr(3,i)=0.0
            go to 500
          end if
c e++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	  if(iac.eq.0)then
	   write(6,*)'no close atom or object for boundary point ',i
	   stop
	  endif
c b+++++++++++++++++++++++++++
c if iac is an object dr has alredy been calculated
c and HAS a DIFFERENT value!!!!!!
          if (iac.le.natom) then
            dr1=xg1-xn1(1,iac)
            dr2=xg2-xn1(2,iac)
            dr3=xg3-xn1(3,iac)
          end if
c e++++++++++++++++++++++++++
          dsr=sqrt(dr1*dr1+dr2*dr2+dr3*dr3)
	  out=.true.
	  if(radpmax.gt.0.0)then
c b++++++++++++++++++++++++++++++
c u should have the same value as previous one
            if (iac.le.natom) then
              u1=xn1(1,iac)+dr1/dsr*r0(iac)
              u2=xn1(2,iac)+dr2/dsr*r0(iac)
              u3=xn1(3,iac)+dr3/dsr*r0(iac)
            else
	      u1=xg1-dr1
              u2=xg2-dr2
	      u3=xg3-dr3
            endif
c e++++++++++++++++++++++++++++++
	    it1=(u1-xo)*cbai
	    it2=(u2-yo)*cbai
	    it3=(u3-zo)*cbai

	    nnbr=0
            liml=cbn1(it1+1+(lcb+1)*it2+(lcb+1)*(mcb+1)*it3)
            limu=cbn2(it1+1+(lcb+1)*it2+(lcb+1)*(mcb+1)*it3)
	    do kk=liml,limu
	      ia=cbal(kk)
              if (ia.le.natom) then
	        dx1=u1-xn1(1,ia)
	        dx2=u2-xn1(2,ia)
                dx3=u3-xn1(3,ia)
                ds2=dx1*dx1+dx2*dx2+dx3*dx3
	        if(ds2.lt.rs2(ia))out=.false.
              else
c b+++++++++++++++++++++++++++
                if (ia.ne.iac.and.(.not.internal(ia-natom))) then
c I want to know if u is within the shell sorrounding the object
                  xq(1)=u1
                  xq(2)=u2
                  xq(3)=u3
                  call distobj(xq,dix,diy,diz,nobject,ia-natom,0.0,dist,
     &  .true.,zeta,axdist)
                  if (dist.ge.0.0.and.dist.lt.radprb(1)) out=.false.
                endif
c e+++++++++++++++++++++++++++++
              end if
	    end do
	  endif

	  if(out)then
            ncbp=ncbp+1
            if (iac.le.natom) then
              vcrd(1,i)=xn1(1,iac)+dr1*rad3(iac)/dsr
              vcrd(2,i)=xn1(2,iac)+dr2*rad3(iac)/dsr
              vcrd(3,i)=xn1(3,iac)+dr3*rad3(iac)/dsr
              vnr(1,i)=dr1/dsr
              vnr(2,i)=dr2/dsr
              vnr(3,i)=dr3/dsr
c b++++++++++++++++++++++++++++
            else
              vcrd(1,i)=xg1-radprb(1)*vnor(1)-dr1          
              vcrd(2,i)=xg2-radprb(1)*vnor(2)-dr2
              vcrd(3,i)=xg3-radprb(1)*vnor(3)-dr3
              vnr(1,i)=vnor(1)
              vnr(2,i)=vnor(2)
              vnr(3,i)=vnor(3)
            end if
c e++++++++++++++++++++++++++++

            atndx(i)=iac
          else
            atndx(i)=0
	  endif
500       continue
	end do
        i_cbn1= memalloc(i_cbn1,0)
        i_cbn2= memalloc(i_cbn2,0)
        i_cbal= memalloc(i_cbal,0)

c scale the re-entrant points with respect to expos
c if radprb = 0.0 we are done.
	if(radpmax.gt.0.0)then
	  iall=0

          cba=1./grdi
	  do 700 i=1,ibnum
c b+++mol. con diversa eps ++++01/02+++++++++++++++
            if(atndx(i).eq.-1) go to 700
c e++++++++++++++++++++++++++++++++++++++++++++++++
	    if(atndx(i).eq.0)then
              s1=vcrd(1,i)*x1+x1x
              s2=vcrd(2,i)*x1+x1y
              s3=vcrd(3,i)*x1+x1z

              xx=(s1-mnx)*grdi
              yy=(s2-mny)*grdi
              zz=(s3-mnz)*grdi
              jx=int(xx)
              jy=int(yy)
              jz=int(zz)
              dx=xx-float(jx)
              dy=yy-float(jy)
              dz=zz-float(jz)
              dmn1=amin1(dx,dy,dz)
              dmx=amax1(dx,dy,dz)
              dmn2=1.0-dmx
              dcr=amin1(dmn1,dmn2)
              ctf=cba*(1+dcr)
              ctf=ctf*ctf
              iacl=0
              rmn=100.
              do jjx=jx-1,jx+1
              do jjy=jy-1,jy+1
              do jjz=jz-1,jz+1
              do ii=iab1(jjx,jjy,jjz),iab2(jjx,jjy,jjz)
                iac= icume(ii)
                dist=(s1-expos(1,iac))**2 +(s2-expos(2,iac))**2 +
     &               (s3-expos(3,iac))**2
                if(dist.lt.rmn)then
                  rmn=dist
                  iacl=iac
                endif
              end do
              end do
              end do
              end do
              if(iacl.gt.0.and.rmn.lt.ctf)goto 300
              do jxi=-2,2
              do jyi=-2,2
              do jzi=-2,2
                if(outcb(jxi,jyi,jzi))then
                  jjx=jx+jxi
                  if(jjx.ge.0.and.jjx.le.lcb1)then
                    jjy=jy+jyi
                    if(jjy.ge.0.and.jjy.le.mcb1)then
                      jjz=jz+jzi
                      if(jjz.ge.0.and.jjz.le.ncb1)then
                        do ii=iab1(jjx,jjy,jjz),iab2(jjx,jjy,jjz)
                          iac= icume(ii)
                          dist=(s1-expos(1,iac))**2 +(s2-expos(2,iac))
     &                            **2 +(s3-expos(3,iac))**2
                          if(dist.lt.rmn)then
                            rmn=dist
                            iacl=iac
                          endif
                        end do
                      endif
                    endif
                  endif
                endif
              end do
              end do
              end do
              if(iacl.gt.0)goto 300
              iall=iall+1

              do iac=1,extot
	        dist=(s1-expos(1,iac))**2 +(s2-expos(2,iac))**2 +
     &               (s3-expos(3,iac))**2
	        if(dist.lt.rmn)then
	          rmn=dist
	          iacl=iac
	        endif
	      end do
300	      continue

              dx=s1-expos(1,iacl)
              dy=s2-expos(2,iacl)
              dz=s3-expos(3,iacl)
	      rdist=sqrt(dx*dx+dy*dy+dz*dz)
	      if(rdist.eq.0) then
	        dist=0.0
	      else
c b+++++++++++++++++++++++++++
c if inside any object, radprb(2)...
                dst=0.
                do ii=1,nobject
                  strtmp=dataobject(ii,1)
                  read(strtmp(16:18),*)kind
                  if (strtmp(1:4).ne.'is a'.and.kind.ne.2) then
                    xq(1)=s1
                    xq(2)=s2
                    xq(3)=s3
                    call distobj(xq,dix,diy,diz,nobject,ii,0.,dst,
     &                          .true.,zeta,axdist)
c assuming that if the VdW point is half grid space into an object
c that means that this belongs to an atom buried in the object
                    if (dst.lt.-hgs) then 
                      dist=radprb(2)/rdist
                      go to 400 
                    end if
                  end if
                end do
c e+++++++++++++++++++++++++++
                dist=radprb(1)/rdist
400             continue
	      end if
              vcrd(1,i)=expos(1,iacl)+dx*dist
              vcrd(2,i)=expos(2,iacl)+dy*dist
              vcrd(3,i)=expos(3,iacl)+dz*dist

              if(rdist.gt.1.0e-8)then
                vnr(1,i)=-dx/rdist
                vnr(2,i)=-dy/rdist
                vnr(3,i)=-dz/rdist
              else
                write(6,*)'bdp close to arcp ',i,rdist
              endif

	    endif
700       continue
	endif
c b++++++++++++++++++++++++++++
        i_internal=memalloc(i_internal,0)
c e++++++++++++++++++++++++++++
c	 do i=1,ibnum
c	 write(2,'(i8,3f12.6,i5)')
c     &	 i,vcrd(1,i),vcrd(1,i),vcrd(1,i),atndx(i)
c	 end do
c	 close (2)
c Varrebbe la pena di capire % of ... cosa significa.
c       write(6,*)'% of boundary points contacting solvent = ',
c    &	float(ncbp)/float(ibnum)*100.
	return
	end
