	subroutine rforce(afield,natom,scspos,scrg,
     &  atsurf,ibnum,atmcrg,xn1,chgpos,nqass,crgatn,nobject)
c
	dimension afield(3,natom+nobject),atmcrg(4,nqass),
     &	chgpos(3,nqass),xn1(3,natom)
	dimension scspos(3,ibnum),scrg(ibnum),sfield(3)
	integer atsurf(ibnum)
	integer crgatn(1)
c
	do i=1,natom
	  afield(1,i)=0.0
	  afield(2,i)=0.0
	  afield(3,i)=0.0
	end do

	do i=1,ibnum
	  sfield(1)=0.0
	  sfield(2)=0.0
	  sfield(3)=0.0
c
	  x=scspos(1,i)
	  y=scspos(2,i)
	  z=scspos(3,i)
	  sc=scrg(i)
c erased some comments (Walter)
c calculate total field on this surface element due to ALL charges
	  do j=1,nqass
	    dist1=(x-chgpos(1,j))
	    dist2=(y-chgpos(2,j))
	    dist3=(z-chgpos(3,j))
c
	    dist=dist1**2+dist2**2+dist3**2
	    sdist=sqrt(dist)
	    temp=atmcrg(4,j)/(dist*sdist)
c
	    sfield(1)=sfield(1)+temp*dist1
	    sfield(2)=sfield(2)+temp*dist2
	    sfield(3)=sfield(3)+temp*dist3
c add negative of this to the charged atom
	    iat=crgatn(j)
c b+++++++++++++++++++++++++++++
          if (iat.lt.0) go to 10
c e++++++++++++++++++++++++++++++
	    if(iat.eq.0)then
	      write(6,*)'problems with crgatn '
	      stop
	    endif

	    afield(1,iat)=afield(1,iat)-sc*temp*dist1
	    afield(2,iat)=afield(2,iat)-sc*temp*dist2
	    afield(3,iat)=afield(3,iat)-sc*temp*dist3

10      continue
	  end do
c
	  sfield(1)=sfield(1)*scrg(i)
	  sfield(2)=sfield(2)*scrg(i)
	  sfield(3)=sfield(3)*scrg(i)
c
	  j=atsurf(i)
c
	  afield(1,j)=afield(1,j)+sfield(1)
	  afield(2,j)=afield(2,j)+sfield(2)
	  afield(3,j)=afield(3,j)+sfield(3)
	end do
	return
	end


c b+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
	subroutine rforceeps1(afield,natom,scspos,scrg,
     &  atsurf,ibnum,atmcrg,xn1,chgpos,nqass,crgatn,nobject)
c
	dimension afield(3,natom+nobject),atmcrg(4,nqass),
     &	chgpos(3,nqass),xn1(3,natom)
	dimension scspos(3,ibnum),scrg(ibnum)
	integer atsurf(ibnum)
	integer crgatn(1)
	real*4 rc
c
	do j=1,nqass
        x=chgpos(1,j)
	  y=chgpos(2,j)
	  z=chgpos(3,j)
	  rc=atmcrg(4,j)
	  iat=crgatn(j)

c calculate total field on this surface element due to ALL charges
	  do i=1,ibnum
	    dist1=(x-scspos(1,i))
	    dist2=(y-scspos(2,i))
	    dist3=(z-scspos(3,i))
c
	    dist=dist1**2+dist2**2+dist3**2
	    sdist=sqrt(dist)
	    temp=scrg(i)/(dist*sdist)
	  end do

        
        if (iat.lt.0) go to 10
        if(iat.eq.0)then
          write(6,*)'problems with crgatn '
          stop
        endif
        afield(1,iat)=rc*temp*dist1
        afield(2,iat)=rc*temp*dist2
        afield(3,iat)=rc*temp*dist3
10      continue

	end do
	return
	end
c e+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++