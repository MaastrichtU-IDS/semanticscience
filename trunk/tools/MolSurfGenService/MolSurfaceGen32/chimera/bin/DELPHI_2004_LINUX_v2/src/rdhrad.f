	subroutine rdhrad(*)
c
	include 'qdiffpar4.h'
	include 'qlog.h'
c
c	character*1 chn
c	character*3 res
c	character*4 rnum
c	character*6 atm
c
	character*80 filnam
	character*60 comment
	logical pK
c
c read radius file and store in hash table
c
	do i=1,nrlist
	irnumb(i)=0
	irlink(i)=0
	end do
c
	open(11,file=siznam(:sizlen),status='old',err=901)
	write(6,*)'atom radii read from file'
	write(6,*)siznam(:sizlen)
	write(6,*)' '
c
c skip/print comments (start with !) and one column header line 
c
105	read(11,201,end=901)comment
	if(comment(1:1).eq.'!') then
	  write(6,*)comment
	  goto 105
	end if
201   format(a)
	inc=index(comment,' ')-1
	if(comment(1:16).eq.'atom__res_radius')then
	pK=.false.
	elseif(comment(1:inc).eq.'atom__resnumbc_radius_')then
	write(6,*)'reading pK style radius file'
	pK=.true.
	else
	write(6,*)'unknown header format in radius file:'
	write(6,*)comment
	stop
	endif
	nrdrec = 0
100   continue
	  nrdrec = nrdrec + 1
	  if(nrdrec.gt.nrmax) then
	    write(6,*)' maximum # of radius records exceeded'
	    write(6,*)' increase nrmax'
	    stop 
	  end if
	  if(pK)then
          read(11,202,err=904,end=300)atm,res,rnum,chn,rad
202       format(A6,A3,A4,A1,F8.3)
          call up(atm,6)
          call elb(atm,6)
          call up(res,3)
          call elb(res,3)
          call up(rnum,4)
          call elb(rnum,4)
          call up(chn,1)
          call elb(chn,1)
          atnam(nrdrec) = atm
          rnam(nrdrec)  = res
          rrnum(nrdrec)  = rnum
          rchn(nrdrec)   = chn
          radt(nrdrec) = rad

	  else

          read(11,200,err=904,end=300)atm,res,rad
          call up(atm,6)
          call elb(atm,6)
          call up(res,3)
          call elb(res,3)
	  rnum = '    '
	  chn = ' '
          atnam(nrdrec) = atm
          rnam(nrdrec)  = res
          rrnum(nrdrec)  = rnum
          rchn(nrdrec)   = chn
          radt(nrdrec)  = rad
	  endif

          call rent(atm,res,rnum,chn,nrdrec)
        goto 100
300   continue
	close(11)
200   format(A6,A3,F8.3)
	nrdrec = nrdrec - 1
	write(6,*)'# of radius parameter records:',nrdrec
c
c
	return
901 	write(6,*) "nonexistence or unexpected end of radius file"
        write(6,*)"This is correct in case there are ONLY objects,"
        write(6,*)"or in case some specific delphi pdb format is used!"
	return  
904	write(6,*) "problem with reading radius file, fort.11"
	return 1
	end
