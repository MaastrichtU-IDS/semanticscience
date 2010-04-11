	subroutine form(fname,nam1,ifrm)
c
	character*80 fname,line,asci
	integer len
	logical ifrm
c
        asci(1:40)="1234567890 .-+#,$asdfghjklzxcvbnmqwertyu"
	asci(41:80)="iopASDFGHJKLZXCVBNMQWERTYUIOP)(}{][/    "
c
204	format(a80)
c
        open(9,file=fname(:nam1),form='formatted')
        read(9,204,err=500,end=600)line
        ias=0
        do i=1,80
        if(index(asci,line(i:i)).eq.0) then
c	write(6,*) line(i:i)
	ias=ias+1
        end if
	end do
c
c	 write(6,*)'ias = ',ias
c	 write(6,*)'temporary fix for dealing with unformatted pdb files
c    &	 have ias less than 10'
c       if(ias.gt.5) then
        if(ias.gt.10) then
        ifrm=.false.
        else
        ifrm=.true.
        end if
	goto 1000
c
500	write(6,*) "unexpected error reading pdb file"
	write(6,*) "assuming formatted file!"
	ifrm=.true.
	goto 1000
c
600	write(6,*) "unexpected end of pdb file!"
	write(6,*) "assuming formatted file!"
	ifrm=.true.
	goto 1000
	
c
1000    close(9)
c
	end
