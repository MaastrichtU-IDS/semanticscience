	subroutine namlen(fname,nlen)
	character*80 fname
	integer nlen
	i=1
100	if(fname(i:i).eq.' ') then
	nlen=i-1
	goto 200
	else
	i=i+1
	goto 100
	end if
200	continue
	return
	end
