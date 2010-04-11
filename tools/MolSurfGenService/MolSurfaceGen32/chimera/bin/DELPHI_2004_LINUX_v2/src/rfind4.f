c--------------------------------------------------------
      subroutine rfind(atm,res,rnum,chn,ifind,n)
c
c	find entry nres in hash table and check match with res
c
	include 'qdiffpar4.h'
c-------------------------------------------------


      n = ichash(atm,res,rnum,chn)
c	check for match
      ifind = 0
100   continue
c	while no match and not at end of link list
      if(irnumb(n).eq.0) then !no match
        ifind = 0
        return
      end if

      if((res.eq.rnam(irnumb(n))).and.(atm.eq.atnam(irnumb(n)))
     &  .and.(rnum.eq.rrnum(irnumb(n))).and.(chn.eq.rchn(irnumb(n)))) 
     &  then
        n = irnumb(n)
        ifind = 1
        return
      else
        if(irlink(n).ne.0) then
          n = irlink(n)
        else
          ifind = 0
          return
        end if
      end if
      go to 100
      end

