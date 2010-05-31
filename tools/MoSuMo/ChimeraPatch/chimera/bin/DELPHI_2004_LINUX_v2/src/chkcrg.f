	subroutine chkcrg(natom,atinf,chrgv4)
	real chrgv4(natom)
	character*15 atinf(natom)
      character*80 line
      character*4 err,strng,resnme,resnum,rsnm
      crgsm=0.0
      rsnm='    '
      resnme='    '
	write(6,*)' '
	do i=1,natom
	crg=chrgv4(i)
      resnum=atinf(i)(12:15)
      strng=atinf(i)(7:10)
      if(resnum.ne.rsnm.or.strng.ne.resnme)then
      if(abs(crgsm).gt.1.0e-4)then
      eror=abs(crgsm)-1.0
      if(abs(eror).gt.1.0e-4)
     &	write(6,10)resnme,rsnm,crgsm
10	format('!!! WARNING: ',2a4,' has a net charge of ',f8.4)
      endif
      resnme=strng
      rsnm=resnum
      crgsm=crg
      else
      crgsm=crgsm+crg
      endif 
	end do
      if(abs(crgsm).gt.1.0e-4)then
      eror=abs(crgsm)-1.0
      if(abs(eror).gt.1.0e-4)
     &  write(6,10)resnme,rsnm,crgsm
      endif
	write(6,*)' '
      end
