	subroutine rdlog(fnma,ifnma)
c
c	attempt to read the file names linked to logical units
c
	character*100 line
	character*50 units
	character*7 fort
	character*2 chun
	character*50 fname
	character*50 fnma(30)
	integer ifnma(30),iuni,unum
100	format(a100)
c
	units="101112131415161718192027"
	unum=24
	call system("ls -l fort.* >& temp0101")
c
20	format(a2)
30	format(i2)
	open(10,file="temp0101")
10	continue
	line=" "
	fname=" "
	read(10,100,end=999) line
c
	fort=line(46:52)
	j=index(units(1:unum),line(51:52))
	if(mod(j,2).ne.1) goto 10
	i=0
300	i=i+1
	fname(i:i)=line(56+i:56+i)
	if(fname(i:i).eq." ") goto 200
c	write(6,*) fname(i:i)
	goto 300
200	continue
	if(i.eq.1) then
	write(6,*) fort," is unlinked "
	else
	chun=units(j:j+1)
c
c NB this internal write statement SHOULD work!
c but it doesnt on the convex. it would on the iris
c
c	write(iuni,20) chun
c
c
	read(chun,30)iuni
	fnma(iuni)=fname(:i-1)
	ifnma(iuni)=i-1
	write(6,*) fort," is linked to ",fnma(iuni)(:ifnma(iuni))
	end if
c
c	write(6,100) line
	goto 10
c
c	
999	continue
	close(10)
c
	call system("rm temp0101")
	return
	end
