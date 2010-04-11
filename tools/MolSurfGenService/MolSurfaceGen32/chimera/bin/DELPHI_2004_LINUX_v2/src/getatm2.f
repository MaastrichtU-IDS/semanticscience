	subroutine getatm(fname,nam1,ifrm,idfrm,iatinf,iatrad,iatcrg,atot,
     &  nmedia,nobject,ndistr,ionlymol,repsin,epkt)

	include "pointer.h"
c
c
c fname= file name, nam1=length of file name
c ifrm = format status of file
c idfrm= type of formatted file
c iatinf= whether there is atom info
c iatrad= whether there is radius info
c iatcrg= whether there is charge info
c atot = number of atoms read in
c atpos= atom coordinates
c rad = radius of atoms
c crg= charge on atoms
c atinf= atom information field
c
c read a pdb file and extract out the coordinates, the atom info
c and optionally the extra two fields
c
	parameter(natmax=100000)
c b+++++++++++++++++++++
        parameter(nmediamax=1000)
        parameter(nobjectmax=1000)
        parameter(ndistrmax=1000)
c e+++++++++++++++++++++
c
	character*80  fname,line,fname2,asci
	character*6 head,cval1
	character*7 cval2
	character*24 crdstr
        character*8 strtmp
	character*26 xfield
	character*12 xnum
	character*15 atminf
	character*10 cnum
	character*26 cap1,cap2
	real xo(3),radx,crgx
	logical ifrm,iatinf,iatrad,iatcrg
c new (instead of include file)
	character*15 atinf(natmax)
c b+++++++++++++++++++
        real medeps(0:nmediamax),repsintmp,epkt,repsin
        integer iatmmed(natmax),nmedia,objecttype           
        integer tmpiatmmed(nobjectmax),nobject
        character*80 dataobject(nobjectmax,2),datadistr(ndistrmax)
        logical ifirst,ionlymol
c iatmmed :vector containing internal media-number per atom and object
c nobject= number of objects, any molecule is counted as an object
c medeps :vector containing correspondence media<->epsilon/epkt
c dataobject: vector containing string with object data, and pre-elab data
c ionlymol: flag : .false. => there are objects other than molecules
c           even if they are charge distributions  
c objecttype : 1-sphere, 2-cilinder --
c datadistr : vector containing string with charge distribution data
c e+++++++++++++++++++
	dimension atpos(3*natmax),chrgv4(natmax),rad3(natmax)
	integer atot
c
	i_atpos=memalloc(i_atpos,4*3*natmax)
	i_rad3=memalloc(i_rad3,4*natmax)
	i_chrgv4=memalloc(i_chrgv4,4*natmax)
	i_atinf=memalloc(i_atinf,-15*natmax)
c b+++++++++++++++++++
        i_medeps=memalloc(i_medeps,4*nmediamax)
        i_dataobject=memalloc(i_dataobject,4*80*nobjectmax*2)
        i_datadistr=memalloc(i_datadistr,4*80*ndistrmax)
        ndistr=0
        ionlymol=.true.
c e+++++++++++++++++++
	iatinf=.false.
	iatrad=.false.
	iatcrg=.false.
c assume default file types, idfrm=0
	idfrm=0
	cnum="0123456789"
c
c assume a formatted file..
	ifrm=.true.
c
	i=0
c
c
204	format(a80)
205	format(3F8.3)
206	format(F7.3)
2062	format(F7.3)
2061	format(F6.2)
207	format(F8.3)
208     format(I3)
c
c open and determine format of file, i.e. formatted or unformatted..
c
	call form(fname,nam1,ifrm)
c
c ifrm=.true. then this is a formatted file
c
	if(ifrm) then
	  write(6,*) "opening formatted file:",fname(:nam1)
 	  open(9,file=fname(:nam1),form='formatted')
	  read(9,204,end=4000,err=4000)line
	  if(index(line,"DELPHI").ne.0) then
	  if(index(line,"PDB").eq.0) then
	    write(6,*) "this is not a delphi pdb file!"
	    write(6,*) "check the file type"
	    goto 999
	  end if
	  write(6,*) "Reading a Delphi-style pdb file"
	  read(9,204,end=4000,err=4000)line
c  look for FORMAT NUMBER=
	  j=index(line,"=")
	  read(line(j+1:80),'(i5)') idfrm
	  write(6,*) "Delphi Format Number = ",idfrm
c b+++++++++++++++++++++++++
          write(6,*)'You are not reading from an objectfile!'
          write(6,*)'Assuming having only molecules, and one medium'
          nmedia=1
          nobject=1
          objecttype=0
          imedianumb=1
          repsintmp=repsin
          medeps(imedianumb)=repsintmp/epkt
          dataobject(nobject,1)="is a molecule    0"
          tmpiatmmed(nobject)=imedianumb
c e+++++++++++++++++++++++++
	end if
c
	if(idfrm.eq.0) then
	atot=0
c b+++++++++++++++++++++++++
        ifirst=.true.
c e+++++++++++++++++++++++++
	iatinf=.true.
	iatrad=.false.
	iatcrg=.false.
502     continue
        head = line(1:6)
	call up(head,6)
c b++++++++++++++++++++++ read from extended pdbfile the media type
        if (ifirst.and.(head.ne.'MEDIA ')) then
          write(6,*)'You are not reading from an objectfile! assuming 
     &  having only molecules, and one dielectric medium'
          nmedia=1
          nobject=1
          objecttype=0
          imedianumb=1
          repsintmp=repsin
          medeps(imedianumb)=repsintmp/epkt
          dataobject(nobject,1)="is a molecule    0"
          tmpiatmmed(nobject)=imedianumb
        end if
        ifirst=.false.

        if((head.ne.'ATOM  ').and.(head.ne.'HETATM').and.(head.ne.
     &  'OBJECT').and.(head.ne.'MEDIA ').and.(head.ne.'CRGDST')) then
        read(9,204,end=2000,err=4000)line
	goto 502
	end if
        if(head.eq.'MEDIA ') then
        strtmp=line(8:10)  
        read(strtmp,208)nmedia
        read(9,204,end=2000,err=4000)line
        goto 502
        end if

        if(head.eq.'OBJECT') then
          strtmp=line(8:10)
          read(strtmp,208)nobject                             
          strtmp=line(12:14)
          read(strtmp,208)objecttype
          strtmp=line(16:18)
          read(strtmp,208)imedianumb
          strtmp=line(20:27)
          read(strtmp,207)repsintmp
          medeps(imedianumb)=repsintmp/epkt
          read(9,204,end=2000,err=4000)line
          if (objecttype.ne.0) then
             ionlymol= .false. 
             dataobject(nobject,1)=line
             read(9,204,end=2000,err=4000)line
          else
            dataobject(nobject,1)="is a molecule    0"
            tmpiatmmed(nobject)=imedianumb
          end if
          goto 502
        end if

        if(head.eq.'CRGDST') then
         ionlymol= .false.
         strtmp=line(8:10)
         read(strtmp,208)ndistr    
         read(9,204,end=2000,err=4000)line
         datadistr(ndistr)=line
         read(9,204,end=2000,err=4000)line
         goto 502
        end if

c e++++++++++++++++++++++
c if not a header line then process
	atot=atot+1
	crdstr=line(31:54)
c b++++++++++++++++++++++                      and put it in iatmmed
        iatmmed(atot)=imedianumb
c e++++++++++++++++++++++
	atinf(atot)=line(12:26)
	read(crdstr,205)xo
	atpos(3*atot-2)=xo(1)
	atpos(3*atot-1)=xo(2)
	atpos(3*atot)=xo(3)
        read(9,204,end=2000,err=4000)line
	goto 502
c end of standard pdb read
	end if
c
	if((idfrm.eq.2).or.(idfrm.eq.1)) then
	iatinf=.true.
	iatrad=.true.
	iatcrg=.true.
	read(9,204,end=4000,err=4000)line
c
c number of atoms given:
c find number
	j=index(line,"=")
	if(j.eq.0) goto 400
c no equals sign,skip precalcualted number of atoms
c
c find first non blank character after equals sign
250	if(line(j+1:j+1).eq." ") then
	j=j+1
	if(j.eq.80) goto 400
c end of line,skip precalcualted number of atoms
	goto 250
	end if
c
	
c check to see if j+1 is numerical..
	if(index(cnum,line(j+1:j+1)).eq.0)goto 400
c  not a number after equals, skip precalcualted number of atoms
	k=j+2
c
c find length of number string
260	if(index(cnum,line(k:k)).eq.0) then
	goto 275
	else
	k=k+1
	goto 260
	end if
c
c string runs from j+1 to k-1
275	continue
        read(line(j+1:k-1),'(i5)') atot
c
	do i=1,atot
	  read(9,204,end=2000,err=4000)line
	  head=line(1:6)
c b++++++++++++++++++++++      
          iatmmed(atot)=imedianumb
c e++++++++++++++++++++++
	  if(idfrm.eq.1) then
	    crdstr=line(31:54)
	    cval1=line(55:60)
	    cval2=line(61:67)
	    read(crdstr,205)xo
	    read(cval1,2061)radx
	    read(cval2,2062)crgx
	  end if
	  if(idfrm.eq.2) then
            crdstr=line(31:54)
            xfield=line(55:80)
            read(crdstr,205)xo
            read(xfield,'(2f12.7)')radx,crgx
	  end if
          rad3(i)=radx
          chrgv4(i)=crgx
          atpos(3*i-2)=xo(1)
          atpos(3*i-1)=xo(2)
          atpos(3*i)=xo(3)
          atinf(i)=line(12:26)
        end do
        goto 2000
c
400	continue
	i=0
	atot=0
330	continue
	head=line(1:6)
        if((head.eq.'ATOM  ').or.(head.eq.'HETATM')) then
	  i=i+1
	  atot=atot+1
c b++++++++++++++++++++++   
          iatmmed(atot)=imedianumb
c e++++++++++++++++++++++
	  if(idfrm.eq.1) then
	    crdstr=line(31:54)
	    cval1=line(55:60)
	    cval2=line(61:67)
            read(crdstr,205)xo
	    read(cval1,2061)radx
	    read(cval2,2062)crgx
	  end if
	  if(idfrm.eq.2) then
            crdstr=line(31:54)
            xfield=line(55:80)
            read(crdstr,205)xo
            read(xfield,'(2f12.7)')radx,crgx
	  end if
	  rad3(i)=radx
	  chrgv4(i)=crgx
	  atpos(3*i-2)=xo(1)
	  atpos(3*i-1)=xo(2)
	  atpos(3*i)=xo(3)
	  atinf(i)=line(12:26)
	end if
	read(9,204,end=2000,err=4000)line
	goto 330
c
	end if
c
	if(idfrm.eq.3) then
	  iatinf=.true.
	  iatrad=.true.
	  iatcrg=.true.
	  read(9,204,end=4000,err=4000)line
	  do j=1,80
	    ic=index(cnum,line(j:j))
	    if(ic.ne.0) then
	      ic=j
	      goto  44
	    end if
	  end do
44        continue
	  read(line(ic:80),'(i5)',err=4000) atot
	  do i=1,atot
c b++++++++++++++++++++++   
            iatmmed(atot)=imedianumb
c e++++++++++++++++++++++
	    read(9,204,end=2000,err=4000)line
	    crdstr=line(31:54)
	    xfield=line(55:80)
	    read(xfield,'(2f12.7)')radx,crgx
	    read(crdstr,205)xo
	    rad3(i)=radx
	    chrgv4(i)=crgx
	    atpos(3*i-2)=xo(1)
	    atpos(3*i-1)=xo(2)
	    atpos(3*i)=xo(3)
	    atinf(i)=line(12:26)
	  end do
	  goto 2000
	end if
c
4000	continue
	write(6,*) "an error occurred in reading this formatted file"
c
2000	continue 
	write(6,*) "number of atoms read in = ",atot
c
c end of formatted read options
	end if
c
	if(.not.ifrm) then
	  atot=0
	  open(9,file=fname(:nam1),form='unformatted')
	  read(9,end=500,err=500) line
	  if(index(line,"DELPHI").eq.0)goto 500
	  if(index(line,"PDB").eq.0) then
	    write(6,*) "this is not a delphi pdb file!"
	    write(6,*) "check the file type"
	    goto 999
	  end if
	  write(6,*) "Reading a Delphi-style pdb file"
	  read(9,end=500,err=500)idfrm
	  write(6,*) "Delphi Format Number= ",idfrm
	  goto 501
500	  continue
	  idfrm=0
	  close(9)
	  open(9,file=fname(:nam1),form='unformatted')
c
501	  if(idfrm.eq.0) then
c b++++++++++++++++++++++++++++++++++++++++++
          write(6,*)'You are not reading from an objectfile! assuming
     &  having only molecules, and one dielectric medium'
            nmedia=1
            nobject=1
            objecttype=0
            imedianumb=1
            repsintmp=repsin
            medeps(imedianumb)=repsintmp/epkt
            dataobject(nobject,1)="is a molecule    0"
            tmpiatmmed(nobject)=imedianumb
c e+++++++++++++++++++++++++++++++++++++++++
	    iatinf=.false.
	    iatrad=.true.
	    iatcrg=.true.
800	    read(9,end=1000,err=3000) xo,radx,crgx
	    atot=atot+1
c b++++++++++++++++++++++                      and put it in iatmmed
        iatmmed(atot)=imedianumb
c e++++++++++++++++++++++
	    atpos(3*atot-2)=xo(1)
	    atpos(3*atot-1)=xo(2)
	    atpos(3*atot)=xo(3)
	    chrgv4(atot)=crgx
	    rad3(atot)=radx
	    goto 800
	  end if
c
	  if(idfrm.eq.1) then
	    read(9,end=3000,err=3000) atot
	    iatinf=.true.
	    iatrad=.true.
	    iatcrg=.true.
	    do i=1,atot
	      read(9,end=3000,err=3000) atminf,xo,radx,crgx
	      atinf(i)=atminf
	      atpos(3*i-2)=xo(1)
	      atpos(3*i-1)=xo(2)
	      atpos(3*i)=xo(3)
	      chrgv4(i)=crgx
	      rad3(i)=radx
	    end do
	  end if
c
c
3000	  continue
	  write(6,*) "an error occured in reading this unformatted file"
1000	  continue
	  write(6,*) "number of atoms read in = ",atot,"unformatted"
	  close(9)
c
c end of unformatted read
	end if
c
	i_atpos=memalloc(i_atpos,4*3*atot)
	i_rad3=memalloc(i_rad3,4*atot)
	i_chrgv4=memalloc(i_chrgv4,4*atot)
	i_atinf=memalloc(i_atinf,-15*atot)
c b+++++++++++++++++++
        do ii=1,nobject
c regardless of being a molecule or not, iatmmed has a field to say
c which is its medium
          iatmmed(atot+ii)=tmpiatmmed(ii) 
c         objects are considered like atoms in this case
        end do
        i_medeps=memalloc(i_medeps,4*nmedia+4)
        i_dataobject=memalloc(i_dataobject,4*80*nobject*2)
        i_datadistr=memalloc(i_datadistr,4*80*ndistr)        
c e+++++++++++++++++++
999	continue
c
	return
	end
