c program to create the accessible surface arcs object-object
c Walter March 3, 2000

#ifdef PC
cDEC$ IF DEFINED (PC)
        recursive subroutine objvertices(nacc,nobject,xmin,xmax,side,h
     &  ,natom,lookmol)
CDEC$ ELSE
#else
	subroutine objvertices(nacc,nobject,xmin,xmax,side,h
     &  ,natom,lookmol)
#endif
CDEC$ END IF

	include 'acc2.h'
        include 'qlog.h'

        integer nobject,objecttype,itmp,etrm(3),natom,nt,numsup
        integer iepsmp(igrid,igrid,igrid,3),epsdim,kind
        logical lookmol,intersdentro,inacqua
        character*80 dataobject(nobject,2)
        character*80 strtmp
        real limobject(nobject,3,2),side,h
        real ro,sro,dx,dy,dz,tmp,dist,xp(3)
        real cubcrd(3),vmin(3),vmax(3),xmin(3),xmax(3)
        real distv(3,4),coeff,zeta,axdist
        real beta,delta,dist1,dist2

        epsdim=natom+nobject+2
        do i=1,3
          etrm(i)=1+int(0.5+(xmax(i)-xmin(i))/side)
        end do
c       now look into the little cubes
c oss. xmin = vettore dei primi centri
        x=xmin(1)
        do 30  i=1,etrm(1)
          y=xmin(2)
          do 20  j=1,etrm(2)
            z=xmin(3)
            do 10 k=1,etrm(3)

c             now (x,y,z) is the little cube center
c             if(abs(x-0.8).le..501*side.and.abs(z-1.8).le..501*side)
c    &then
c               write(6,*)'ci siamo',x,y,z,side
c               if (side.eq..65) then
c                 write(6,*)''
c               end if
c               if (x.gt.0.8.and.z.gt.1.8) then
c                 write(6,*)''
c               end if
c             end if
              if (side.le.h.and.lookmol) then
c               in order to see if this cube is inside a molecule
c               find the closest midpoint (here vmin/vmax used by chance)
                lookmol=.false.
                vmin(1)=x
                vmin(2)=y
                vmin(3)=z
                call ctog(vmin,vmax)
                ix=int(vmax(1)+.5)
                iy=int(vmax(2)+.5)
                iz=int(vmax(3)+.5)
c               now vmax is in the h-sized cube system
                dx=vmax(1)-ix
                dy=vmax(2)-iy
                dz=vmax(3)-iz
                sro=dx*dx+dy*dy
                ro=sqrt(sro+dz*dz)
                sro=sqrt(sro)
c reasonably approximated algorithm, being the exact one too expensive
                if (sro.eq.0.) then
                   if (dz.ge.0.) then
                      nt=iepsmp(ix,iy,iz,3)
                   else
                      nt=iepsmp(ix,iy,iz-1,3)
                   end if
                else
                  if (abs(dz/ro).lt.0.5) then
                    if(dx/sro.lt.-0.707) nt=iepsmp(ix-1,iy,iz,1)
                    if(dy/sro.lt.-0.707) nt=iepsmp(ix,iy-1,iz,2)
                    if(dx/sro.ge.0.707) nt=iepsmp(ix,iy,iz,1)
                    if(dy/sro.ge.0.707) nt=iepsmp(ix,iy,iz,2)
                  else
                    nt=iepsmp(ix,iy,iz-1,3)
                    if(dz.gt.0.) nt=iepsmp(ix,iy,iz,3)
                  end if
                end if
                nt=mod(nt,epsdim)
c modif pori: qui si aspetta di vedere atomi ma vede anche pori!!??
                if (nt.le.natom+1.and.nt.gt.0) goto 10
              end if 
c calculate if the object surf close to the cube are more or less than 2
              numsup=0
c for objects, only water probes involved
              tmp=radprb(1)+0.5*side
              do 300 ii=1,nobject
                strtmp=dataobject(ii,1)
                read(strtmp(16:18),*)kind
                if (kind.eq.3) write(6,*)'uffaaaaaaaaaaaaaaaaa'
                if (strtmp(1:4).ne.'is a'.and.kind.ne.2) then
                  if ((x.lt.limobject(ii,1,1)-tmp).or.
     &                (y.lt.limobject(ii,2,1)-tmp).or.
     &                (z.lt.limobject(ii,3,1)-tmp).or.
     &                (x.gt.limobject(ii,1,2)+tmp).or.
     &                (y.gt.limobject(ii,2,2)+tmp).or.
     &                (z.gt.limobject(ii,3,2)+tmp).or.
     &                 numsup.gt.2 ) go to 300

                  xp(1)=x
                  xp(2)=y
                  xp(3)=z
                  call distobj(xp,dx,dy,dz,nobject,ii,radprb(1),dist,
     &  .false.,zeta,axdist)
                  if (abs(dist).lt.0.86603*side) then
c sto guardando se sta nella sfera circoscritta
                    numsup=numsup+1
                    distv(numsup,1)=dx
                    distv(numsup,2)=dy
                    distv(numsup,3)=dz
                    distv(numsup,4)=dist
                  end if
                end if
300           continue

              if((numsup.gt.2.and.side.gt.sidemin).or.(numsup.eq.2
     &  .and.side.gt.sideinter)) then
350             continue
c se side successivo e' un quarto dell'attuale allora 1/2-1/8
c               tmp=0.375*side
                tmp=0.25*side
                vmin(1)=x-tmp
                vmin(2)=y-tmp
                vmin(3)=z-tmp
                vmax(1)=x+tmp
                vmax(2)=y+tmp
                vmax(3)=z+tmp
c               call objvertices(nacc,nobject,vmin,vmax,.25*side,h
                call objvertices(nacc,nobject,vmin,vmax,.5*side,h
     &                           ,natom,lookmol)
              else  
                if(numsup.eq.2.and.side.le.sideinter) then
c calculate the closest intersection between the two surfaces
                  dot=distv(1,1)*distv(2,1)+distv(1,2)*distv(2,2)+
     &                distv(1,3)*distv(2,3)
                  tmp=1.-dot*dot
                  if(tmp.le.tol) go to 400
                  coeff=1./tmp
                  dist1=distv(1,4)
                  dist2=distv(2,4)
                  delta=(dist2*dot-dist1)*coeff
                  beta=(dist2-dist1*dot)*coeff
                  intersdentro=(4*(delta**2+beta**2-2*delta*beta*dot).
     &                         le.3*side**2)
                  if (.not.intersdentro) go to 400
c oss inacqua significa al di fuori della VdW Surface
                  inacqua=(dist1.ge.0..and.dist2.ge.0.)
                  if (intersdentro.and..not.inacqua.and.side.gt.sidemin)
     &               go to 350
c                   vai avanti a dividere 

                  if(intersdentro.and.inacqua)then
                    dx=delta*distv(1,1)-beta*distv(2,1)
                    dy=delta*distv(1,2)-beta*distv(2,2)
                    dz=delta*distv(1,3)-beta*distv(2,3)
c vedere se non e' falso positivo di vertice 
                    tmp=.5*side+tol
                    if (abs(dx).le.tmp.and.abs(dy).le.tmp.
     &and.abs(dz).le.tmp.and.abs(delta*beta).gt.tol)then

c if it is inside, then let's write it!
                      nacc=nacc+1
                      expos(1,nacc)=dx+x
                      expos(2,nacc)=dy+y
                      expos(3,nacc)=dz+z
c                      if (debug)then
c                       write(6,*)side,x,y,z
c      write(6,'(A6,I4,5f14.10)')'expos:',nacc,dx+x,dy+y,dz+z,delta,beta
c                      end if
                    end if
                  end if
400               continue
                end if
              end if
c in any other case skip this cube
c NOTE: I am skipping also in case there are 3 surfaces and side< sidemin!!!
              z=z+side
10          continue
            y=y+side
20        continue
          x=x+side
30      continue

        return
        end
        
