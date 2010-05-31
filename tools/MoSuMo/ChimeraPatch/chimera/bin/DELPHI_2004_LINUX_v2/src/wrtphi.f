	subroutine wrtphi
c
cNB uses phimap3 as a temp storage for phimap incase
c want to write not potentials bu salt concentraions
c
	include "qdiffpar4.h"
	include "qlog.h"
        parameter (mgrid=65)
c
        real phimap(igrid,igrid,igrid),phimap3(ngp),phimap4(1)
	character*80 filnam
	character*10 nxtlbl
c
	if(iconc) then
        i_phimap3= memalloc(i_phimap3,4*ngp)
	i=1
	do iz=1,igrid
	do iy=1,igrid
	do ix=1,igrid
	phimap3(i)=phimap(ix,iy,iz)
	i=i+1
	end do
	end do
	end do
	call phicon
	end if
c
	if(ibios) then
c
c write phimap in insight format
c
	  open(14,file=phinam(:philen),form="unformatted")
	  filnam = ' '
	  inquire(14,name = filnam)
	  write(6,*)'potential map written in INSIGHT format to file'
	  write(6,*)filnam
	  write(6,*)'  '
	  ivary = 0
	  nbyte = 4
	  intdat = 0
	  xang = 90.
	  yang = 90.
	  zang = 90.
	  intx = igrid - 1
	  inty = igrid - 1
	  intz = igrid - 1
	  xmax = 0.
	  do 9040 k = 1,3
	    temp = abs(oldmid(k))
	    xmax = amax1(xmax,temp)
9040	  continue
	  range = (igrid-1.)/(2.*scale)
	  extent = range + xmax
	  xstart = (oldmid(1)-range)/extent
	  ystart = (oldmid(2)-range)/extent
	  zstart = (oldmid(3)-range)/extent
	  xend = (oldmid(1)+range)/extent
	  yend = (oldmid(2)+range)/extent
	  zend = (oldmid(3)+range)/extent
        write(14)toplbl
	  write(14)ivary,nbyte,intdat,extent,extent,extent,
     1  xang,yang,zang,xstart,xend,ystart,yend,zstart,
     1  zend,intx,inty,intz
	  do 9041 k = 1,igrid
	    do 9042 j = 1,igrid
		write(14)(phimap(i,j,k),i=1,igrid)
9042	  continue
9041	  continue
c
	elseif(phifrm.eq.2)then
c GRASP phimap - output a 65^3 grid and leave out ngrid spec.
c
          write(6,*)'  '
          write(6,*)'writing potential map in GRASP format'
          write(6,*)'  '
c
          i_phimap4=memalloc(i_phimap4,4*mgrid*mgrid*mgrid)
          call expand(mgrid)
          open(14,file=phinam(:philen),form="unformatted")
          filnam = ' '
          inquire(14,name = filnam)
          write(6,*)'potential map written to file'
          write(6,*)filnam
          write(6,*)'  '
          if(iconc.and.(rionst.ne.0)) then
          nxtlbl="concentrat"
          else
          nxtlbl="potential "
          end if
        write(14)'now starting phimap '
        write(14)nxtlbl,toplbl
c        write(14)phimap4
        call wrtphimap(mgrid,phimap4)
        write(14)' end of phimap  '
        write(14)scale,oldmid
        close(14)
          i_phimap4=memalloc(i_phimap4,0)
c
        else
c
	  write(6,*)'  '
	  write(6,*)'writing potential map in DELPHI format'
	  write(6,*)'  '
c
	  open(14,file=phinam(:philen),form="unformatted")
	    filnam = ' '
	    inquire(14,name = filnam)
	    write(6,*)'potential map written to file'
	    write(6,*)filnam
  	    write(6,*)'  '
  	    if(iconc.and.(rionst.ne.0)) then
  	      nxtlbl="concentrat"
  	    else
	      nxtlbl="potential "
	    end if
            write(14)'now starting phimap '
            write(14)nxtlbl,toplbl
            write(14)phimap
            write(14)' end of phimap  '
            write(14)scale,oldmid,igrid
          close(14)
	end if
c
c b ++++++debug++++++++++++
c       open(52,FILE='phiwalt')
c       do ix=1,65
c            do iz=1,65
c              write(52,*)phimap(ix,33,iz)
c            end do
c       end do
c       close (52)
c  e +++++++++++++++++++++++

	if(iconc) then
	i=1
	do iz=1,igrid
	do iy=1,igrid
	do ix=1,igrid
	phimap(ix,iy,iz)=phimap3(i)
	i=i+1
	end do
	end do
	end do
        i_phimap3= memalloc(i_phimap3,0)
	end if
c
	return
	end

        subroutine wrtphimap(mgrid,phimap)
        real phimap(mgrid,mgrid,mgrid)
        write(14)phimap
        return
        end

        subroutine wrtphiForGUI
c
        include "qdiffpar4.h"
        include "qlog.h"
c
        real phimap(igrid,igrid,igrid)
c b++++++++++++++walter++++write potential map for the GUI
c       open(52,FILE="phimap",form='unformatted')
c       write(52)phimap
c       close(52)
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++
        return
        end


