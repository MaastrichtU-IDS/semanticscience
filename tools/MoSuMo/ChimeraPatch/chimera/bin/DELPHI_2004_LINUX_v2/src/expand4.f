	subroutine expand(mgrid)
c
c expands igrid**3 grid to ngrid**3
c grid (65**3 default) to give compatibilty with previous
c phimap and epsmap formats using trilinear interpolation
	include 'qdiffpar4.h'
	include 'qlog.h'
c
        real phimap(igrid,igrid,igrid),phimap4(mgrid,mgrid,mgrid)
	dimension gc(3),temp(3,ngrid)
c
	rscale = (igrid-1.)/(mgrid-1.)
c
c do high end first to prevent overwriting
c find small grid values and interpolate into big grid
c
	if(igrid.eq.mgrid)then
	  do iz=1,igrid
	  do iy=1,igrid
	  do ix=1,igrid
	     phimap4(ix,iy,iz) = phimap(ix,iy,iz)
	  end do
	  end do
	  end do
	else
	  if(.not.ibios) then
	    do 9000 iz = mgrid,1,-1
	      gc(3) = (iz-1)*rscale + 1.
	      do 9001 iy = mgrid,1,-1
	        gc(2) = (iy-1)*rscale + 1.
	        do 9002 ix = mgrid,1,-1
	          gc(1) = (ix-1)*rscale + 1.
		    call phintp(gc,phiv)
		    phimap4(ix,iy,iz) = phiv
9002		  continue
9001	      continue
9000	    continue
	  end if
	end if
c
c dielectric map
c
c	do 9003 iz = mgrid,1,-1
c	  igz = (iz-1)*rscale + 1.
c	  do 9004 iy = mgrid,1,-1
c	    igy = (iy-1)*rscale + 1.
c	    do 9005 ix = mgrid,1,-1
c	      igx = (ix-1)*rscale + 1.
c		temp(1,ix) = iepsmp(igx,igy,igz,1)
c		temp(2,ix) = iepsmp(igx,igy,igz,2)
c		temp(3,ix) = iepsmp(igx,igy,igz,3)
c9005		  continue
c	   do 9006 ix=mgrid,1,-1
c		iepsmp(ix,iy,iz,1)=temp(1,ix)
c		iepsmp(ix,iy,iz,2)=temp(2,ix)
c		iepsmp(ix,iy,iz,3)=temp(3,ix)
c9006	          continue
c9004	      continue
c9003	    continue
c
c recalculate scale for expanded grids
c
	scale = scale/rscale
	write(6,*)'new scale is ',scale,' grids/ang'
	return
	end
