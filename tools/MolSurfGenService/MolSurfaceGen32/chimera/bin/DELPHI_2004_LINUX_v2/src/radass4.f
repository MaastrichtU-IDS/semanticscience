	subroutine radass(atm,res,rnum,chn,rad,norad)
c
c here the actual assignment from the hash tables is made
	include "qdiffpar4.h"
c
	character*3 tres
       	character*6 tatm
	character*1 achn
 	character*3 ares
 	character*4 arnum
c
	norad=0
          call rfind(atm,res,rnum,chn,ifind,n)
          if(ifind.eq.0) then
            achn = ' '
            call rfind(atm,res,rnum,achn,ifind,n)
            if(ifind.eq.0) then
              arnum = '    '
              call rfind(atm,res,arnum,achn,ifind,n)
              if(ifind.eq.0) then
                ares = '   '
                call rfind(atm,ares,arnum,achn,ifind,n)
                if(ifind.eq.0) then
                  tatm = atm(1:1)//'     '
                  call rfind(tatm,ares,arnum,achn,ifind,n)
	          if(ifind.eq.0) then
	            norad=1
	    	    n=1
		  end if
                end if
              end if
            end if
          end if
c
	  rad = radt(n)
c
	return
	end
