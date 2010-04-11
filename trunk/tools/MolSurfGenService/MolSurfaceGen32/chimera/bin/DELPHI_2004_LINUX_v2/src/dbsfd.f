	subroutine dbsfd(dbval,sfd)
c
	include "qlog.h"
	dimension dbval(0:1,0:6,0:1),sfd(5,0:1)
c 
	debfct = epsout/(deblen*scale)**2
	difeps=epsin-epsout
	sixeps=epsout*6.0
	sixth=1.0/6.0
c
	if(rionst.gt.0.) then
	  do 491 iz=0,1
	    do 493 ix=1,3
	      denom= sixeps + ix*difeps + iz*debfct
	      dbval(0,ix,iz)= 0.0
	      dbval(1,ix,iz)= difeps/denom
	      sfd(ix,iz)=epsout/denom
493	    continue
491	  continue
	  do 492 iz=0,1
	    do 494 ix=4,5
	      denom= sixeps + ix*difeps + iz*debfct
	      dbval(1,ix,iz)= 0.0
	      dbval(0,ix,iz)= -difeps/denom
	      sfd(ix,iz)=epsin/denom
494	    continue
492	  continue
	else
	  do 591 iz=0,1
	    do 593 ix=1,5
	      denom= sixeps + ix*difeps 
	      dbval(0,ix,iz)= (epsout/denom) -sixth 
	      dbval(1,ix,iz)= (epsin/denom) - sixth
593	    continue
591	  continue
	end if
c
c	write(6,200) (((dbval(i,j,k),j=0,6),i=0,1),k=0,1)
c200	format(6f12.7)
	return
	end
