	subroutine epsmak(ibnum,natom,oldmid,uniformdiel,ionlymol,
     &  nobject,nmedia,numbmol)
c
	include 'qlog.h'
	include 'acc2.h'
c
	real atpos(3,natom),xn2(3,natom),rad3(natom),scspos(1)
	integer iepsmp(igrid,igrid,igrid,3)
        logical*1 idebmap(igrid,igrid,igrid)
	integer ibgrd(1),limeps(2,3)
c,ibnd(1)
	integer atsurf(1)
        real oldmid(3)
c b+++++++++
        integer uniformdiel,nobject,nmedia
        real limobject(nobject,3,2),rmid
        character*80 dataobject(nobject,2)
        character*80 strtmp
        integer bndeps(1,1),ibmx,numbmol
        real limgunit(3,2,1) 
	  logical ionlymol
        i_bndeps= memalloc(i_bndeps,4*2*igrid*igrid*igrid)
        i_limgunit=memalloc(i_limgunit,6*4*nobject)
        ibmx=700000
c +++++++++here limobject is expressed in grid units++++
        rmid=float((igrid+1)/2)
        do ii=1,nobject
          do i=1,3
          limgunit(i,1,ii)=(limobject(ii,i,1)-oldmid(i))*scale+rmid
          limgunit(i,2,ii)=(limobject(ii,i,2)-oldmid(i))*scale+rmid
          end do
        end do

c save file datadelphi, containing some variables, to be used by GUI
c       open(52,file='datadelphi',form='unformatted')
c       write(52)igrid
c       write(6,*)limgunit
c       write(6,*)oldmid
c       write(6,*)scale
c       write(52)nobject
c       write(6,*)limobject
c       write(52)dataobject
c       close(52)

c e++++++++++++++++++++++++++++++++++++++++++++++++++++++
c       write(6,*)'limobject'
c       write(6,*)limobject
c       write(6,*)'limgunit'
c       write(6,*)limgunit
	if(uniformdiel) then
	write(6,*) "not going to calculate boundary elements since"
	write(6,*) "uniform dielectric"
	ibnum=0
	goto 999
	end if
c
c lepsx.y.z and uepsx.y.z should be the upper and lower limits of the
c expanded box. if the molecule is smaller than this then reduce leps 
c and upeps accordingly
c note leps/ueps not yet defined..
c
        xmin=limgunit(1,1,1)
        ymin=limgunit(2,1,1)
        zmin=limgunit(3,1,1)
        xmax=limgunit(1,2,1)
        ymax=limgunit(2,2,1)
        zmax=limgunit(3,2,1)

c b++++++++++++++++++++
c find global limits IN GRID UNITS, both, molecule and objects, are considered
        do ii=2,nobject
          xmin=min(xmin,limgunit(1,1,ii))
          ymin=min(ymin,limgunit(2,1,ii))
          zmin=min(zmin,limgunit(3,1,ii))
          xmax=max(xmax,limgunit(1,2,ii))
          ymax=max(ymax,limgunit(2,2,ii))
          zmax=max(zmax,limgunit(3,2,ii))
        end do
        rmax=rdmx
c e+++++++++++++++++++
c       do i=1,natom
c       xmin=min(xn2(1,i),xmin) etc...
c       xmax=max(xn2(1,i),xmax)etc...
c       rmax=max(rad3(i),rmax)
c       end do	

	if(rionst.ne.0.)rmax=max(rmax,exrad)
	rmax=rmax*scale
	xmin=xmin-rmax
	ymin=ymin-rmax
	zmin=zmin-rmax
	xmax=xmax+rmax
	ymax=ymax+rmax
	zmax=zmax+rmax
	limeps(1,3)=max(int(zmin)-2,1)
	limeps(1,2)=max(int(ymin)-2,1)
	limeps(1,1)=max(int(xmin)-2,1)
	limeps(2,3)=min(int(zmax)+2,igrid)
	limeps(2,2)=min(int(ymax)+2,igrid)
	limeps(2,1)=min(int(xmax)+2,igrid)
c       i_ibnd= memalloc(i_ibnd,4*3*7000)
c
	do k=1,igrid
	do j=1,igrid
	do i=1,igrid
c  point is out of any kind of object (probably in solution)
c b+++++++++++++++++++
c          iepsmp(i,j,k,1)=0 no longer needed, calloc superseded malloc
c          iepsmp(i,j,k,2)=0 no longer needed, calloc superseded malloc
c          iepsmp(i,j,k,3)=0 no longer needed, calloc superseded malloc
           idebmap(i,j,k)=1
c e+++++++++++++++++++
	end do
	end do
	end do
c
c hgrl=1./2./scale
c if radprb is less than half of grid spacing, then use old algorithm
c (sri 29March 93)
c The new algorithm should be able to handle all scales; still remains to be
c tested (Sri Apr 95)
c
	finish=cputime(start)
	write(6,*) 'start vw surface at ',finish 
	call setout(natom,0.0,exrad,scale,igrid,nobject,oldmid)
	finish=cputime(start)
	write(6,*) 'fill in re-entrant regions at ',finish 
c       i_ibnd= memalloc(i_ibnd,4*3*ibmx)
        i_limgunit=memalloc(i_limgunit,0)
	call vwtms(ibnum,atpos,natom,oldmid,limeps,ionlymol,nmedia
     &  ,nobject,ibmx,numbmol)
c       i_ibnd= memalloc(i_ibnd,0)

	finish=cputime(start)
	if(.not.isrf)
     &	write(6,*) 'time to turn everything in is',finish 
c
c comment out membrane stuff for a moment..
c	 if(imem) call mkmem
c
999	continue
	return
	end
