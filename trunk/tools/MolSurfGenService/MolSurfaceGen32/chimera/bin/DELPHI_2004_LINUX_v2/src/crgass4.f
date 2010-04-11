	subroutine crgass(atm,res,rnum,chn,crg)
c
c actual charge assignment from the hash tables...
	include "qdiffpar4.h"
c
	character*3 sres
	character*1 schn
	character*4 snum
c
c	character*1 chn
c	character*3 res
c	character*4 rnum
c	character*6 atm
c
c
c assignchargeto atom, searching for decreasingly specific specification
c kas,29jn 89- add extra searches with wild card:
c search order:  atom, res, num, chain
c		      x     x    x   x
c			x     x    x   
c			x     x        x
c			x     x
c			x          x   x
c			x          x
c			x              x
c			x
c
c note if no charge record found, is assumed to be 0.0
c
	  call cfind(atm,res,rnum,chn,ifind,n)
	  if(ifind.eq.0) then
	    schn = chn
	    chn = ' '
	    call cfind(atm,res,rnum,chn,ifind,n)
	    if(ifind.eq.0) then
		chn = schn
		snum = rnum
		rnum = '    '
	      call cfind(atm,res,rnum,chn,ifind,n)
	      if(ifind.eq.0) then
	        schn = chn
	        chn = ' '
	        call cfind(atm,res,rnum,chn,ifind,n)
		  if(ifind.eq.0) then
		    chn = schn
		    rnum = snum
		    sres = res
		    res = '   '
	          call cfind(atm,res,rnum,chn,ifind,n)
	          if(ifind.eq.0) then
	            schn = chn
	            chn = ' '
	            call cfind(atm,res,rnum,chn,ifind,n)
	            if(ifind.eq.0) then
		        chn = schn
		        snum = rnum
		        rnum = '    '
	              call cfind(atm,res,rnum,chn,ifind,n)
	              if(ifind.eq.0) then
	                schn = chn
	                chn = ' '
	                call cfind(atm,res,rnum,chn,ifind,n)
			  endif
			endif
		    endif
		  end if
		end if
	    end if
	  end if
c
	if(ifind.ne.0) then
	crg=chrgvt(n)
	else
	crg=0.0
	end if
c
	return
	end
