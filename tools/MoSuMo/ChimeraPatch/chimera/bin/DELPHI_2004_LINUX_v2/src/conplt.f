	subroutine conplt(array,title,iclr,iscl,imk,iplt,
     1 symb,ixmin,ixmax,iplot,ymin,ymax)
c
c produces line plot of array
c
	parameter ( nxran = 60 )
	parameter ( nyran = 20 )
	dimension array(nxran)
	character*1 line(nxran),symb
	character*70 iplot(nyran),title
	data line / nxran*'-'/
c------------------------------------------------------
	if(iclr.eq.1) then
c
c clear plot
c
	    ymin = 1.e10
	    ymax = 0.0
	    do 9000 i = 1,nyran
	      iplot(i) = ' '
9000	    continue
	end if
	if(iscl.eq.1) then
c
c scale plot
c find max, min of data
c
	    do 9001 i = 1,nxran
	      if(array(i).gt.0.0) then
	        ymin = min(ymin,array(i))
	        ymax = max(ymax,array(i))
	      end if
9001	    continue
c
c find y plot range in log scale
c

	    yminl = alog10(ymin)
	    ymaxl = alog10(ymax)
	    iyup = (1. + ymaxl)
	    iylw = (yminl - 1)
	    iyran = iyup - iylw
	end if
	if(imk.eq.1) then
c
c make plot
c
c
c stick x values in the appropriate bins after clipping
c
	    yminl = alog10(ymin)
	    ymaxl = alog10(ymax)
	    iyup = (1. + ymaxl)
	    iylw = (yminl - 1)
	    iyran = iyup - iylw
	    do 9002 i = 1,nxran
		if((array(i).ge.ymin).and.(array(i).le.ymax)) then
	        temp = alog10(array(i))
	        temp1 = (temp - iylw)/iyran
	        ibin = temp1*(nyran - 1) + 1
	        iplot(ibin)(i:i)= symb
		end if
9002	    continue
	end if
	if(iplt.eq.1) then
c
c draw out plot
c
	    write(6,*)'  '
	    write(6,204)title
204	    format(5X,A70)
	    write(6,200)ymax,line
200       format(' ',g9.2,' |-',60A,'-|')
	    do 9003 i = nyran,1,-1
	      write(6,201)iplot(i)
201	      format(11X,'| ',A60,' |')
9003	    continue
	    write(6,200)ymin,line
	    write(6,203)
203	    format(11X,'|',62X,'|')
	    write(6,202)ixmin,ixmax
202	    format(6X,I5,58X,I5)
	end if
	return
	end
