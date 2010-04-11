	subroutine extrmobjects(nobject,scale,natom,numbmol)

        include 'acc2.h'
        integer nobject,count,objecttype,i,natom,numbmol
        character*80 dataobject(nobject,2)
        character*80 strtmp
        real limobject(nobject,3,2),xb(3),xa(3),tmpvect(3),tmp,radius 
        real alpha,xc(3),xd(3),sign,tmpvect1(3),tmpvect2(3),scale
        real modul,modul2,tmp1
        real atpos(3,natom),rad3(natom),tmp2
c limobject contains extreme values of each object 
c  for a molecule it has extreme but without radii
c  descritpion:   limobject(object number,coord,min_max)

c
c find extrema of each object and  according to them 
c 
        numbmol=0
        rdmx=0.01
        do count=1,nobject
c extracts object type number
           strtmp=dataobject(count,1)

           if (strtmp(1:4).eq.'is a') then          
c here we have a molecule, calculating also max radius
              numbmol=numbmol+1
              write(6,*)"object number :   ",count,",  is a molecule"    
              if (natom.eq.0) then
                write(6,*)'a molecule with no atoms?'
                stop
              end if
              do i=1,3
                limobject(count,i,1)=atpos(i,1)
                limobject(count,i,2)=atpos(i,1)
              end do
              rdmx=rad3(1)
              do 2103 ix=2,natom
                do i=1,3
              limobject(count,i,1)=min(limobject(count,i,1),atpos(i,ix))
              limobject(count,i,2)=max(limobject(count,i,2),atpos(i,ix))
                end do
                rdmx=amax1(rdmx,rad3(ix))
2103          continue

           else
              read(strtmp(8:10),'(I3)')objecttype
c now deals with different types of objects

              if (objecttype.eq.1) then
c here we have a sphere
                 write(6,*)"object number :   ",count,",  is a sphere"      
                 write(6,*)strtmp
                 read(strtmp(20:80),*)xb,radius
                 if (radius.le.1./scale) write(6,*)"WARNING! geometric
     &   parameter too small to be 'resolved' by the program"
                 do i=1,3
                    limobject(count,i,1)=xb(i)-radius
                    limobject(count,i,2)=xb(i)+radius
                 end do
              end if             

              if (objecttype.eq.2) then
c here we have a cylinder
                 write(6,*)"object number :   ",count,",  is a cylinder"
                 write(6,*)strtmp
                 read(strtmp(20:80),*)xa,xb,radius 
                 call diffvect(xa,xb,tmpvect)
                 call inner(tmpvect,tmpvect,modul2)
                 modul=sqrt(modul2)
                 write(dataobject(count,2),'(5f8.3)')tmpvect,modul,
     & modul2
                 if((radius.le.1./scale).or.(modul2.le.1./(scale**2)))
     &            write(6,*)"WARNING! geometric
     &   parameter too small to be 'resolved' by the program"
                 do i=1,3
                    tmp1=tmpvect(i)*tmpvect(i)
                    tmp=sqrt(modul2-tmp1)/modul
                    tmp=radius*tmp
                    limobject(count,i,1)=-tmp+xb(i)+min(0.,tmpvect(i))
                    limobject(count,i,2)=tmp+xb(i)+max(0.,tmpvect(i))
                 end do 
              end if

              if (objecttype.eq.3) then
c here we have a cone
                 write(6,*)"object",count,"     is a cone"
                 write(6,*)strtmp
                 read(strtmp(20:80),*)xa,xb,alpha 
c                xa=coordinates of the tip   
c                alpha is expressed in degrees, so it needs a conversion
                 alpha=alpha*3.1415/180.
                 call diffvect(xa,xb,tmpvect)
                 call inner(tmpvect,tmpvect,modul2)
                 write(dataobject(count,2),'(5f8.3)')tmpvect,sqrt(
     &  modul2),modul2
                 if (modul2.le.1./(scale**2))write(6,*)"WARNING! 
     &   geometric parameter too small to be 'resolved' by the program"
                 do i=1,3
                  tmp1=tmpvect(i)*tmpvect(i)
                  tmp=sqrt(modul2-tmp1)
                  tmp=tmp*tan(alpha)
                  limobject(count,i,1)=-tmp+xb(i)+min(0.,tmpvect(i)+tmp)
                  limobject(count,i,2)=tmp+xb(i)+max(0.,tmpvect(i)-tmp)
                 end do
              end if

              if (objecttype.eq.4) then
c here we have a box 
                 write(6,*)"object number :   ",count,",  is a box"
                 write(6,*)strtmp
                 read(strtmp(20:80),*)xa,xb,xc,xd

                 call diffvect(xd,xa,tmpvect)
                 call inner(tmpvect,tmpvect,tmp)
                 if (tmp.le.1./(scale**2))write(6,*)"WARNING! geometric
     &   parameter too small to be 'resolved' by the program"

                 call diffvect(xc,xa,tmpvect2)
                 call inner(tmpvect2,tmpvect2,tmp2)
                 if (tmp2.le.1./(scale**2))write(6,*)"WARNING! geometric
     &   parameter too small to be 'resolved' by the program"

                 call diffvect(xb,xa,tmpvect1)
                 call inner(tmpvect1,tmpvect1,tmp1)
                 if (tmp1.le.1./(scale**2))write(6,*)"WARNING! geometric
     &   parameter too small to be 'resolved' by the program"

                 write(dataobject(count,2),'(12f6.3)')tmpvect,sqrt(tmp),
     &  tmpvect2,sqrt(tmp2),tmpvect1,sqrt(tmp1)

c                partial conversion to axial
                 call addvect(xc,xb,xb)
                 call mul(0.5,xb,xb)
                 call addvect(xb,tmpvect,xa)

c now tmpvect=A-B; tmpvect1=C-D ; tmpvect2=E-C (axial notation)
c axial changes only A->(B+C)/2+D-A and B->(B+C)/2
                 do i=1,3
c find the minimum
                   tmp=xa(i)
                   if (tmpvect(i).gt.0.0) tmp=xb(i)
                   sign=0.5
                   if (tmpvect1(i).gt.0.0) sign=-0.5
                   tmp=tmp+sign*tmpvect1(i)
                   sign=0.5
                   if (tmpvect2(i).gt.0.0) sign=-0.5
                   tmp=tmp+sign*tmpvect2(i)
                   limobject(count,i,1)=tmp
c find the maximum
                   tmp=xa(i)
                   if (tmpvect(i).lt.0.0) tmp=xb(i)
                   sign=0.5
                   if (tmpvect1(i).lt.0.0) sign=-0.5
                   tmp=tmp+sign*tmpvect1(i)
                   sign=0.5
                   if (tmpvect2(i).lt.0.0) sign=-0.5
                   tmp=tmp+sign*tmpvect2(i)
                   limobject(count,i,2)=tmp
                 end do
              end if

           end if
        end do
	return
	end

        subroutine inner(v,u,dot)
c calculate the inner procuct between u and v vectors
        real u(3),v(3),dot

        dot=u(1)*v(1)+u(2)*v(2)+u(3)*v(3)
        return
        end

        subroutine diffvect(v,u,w)
c vector w = v-u
        real v(3),u(3),w(3)
        integer i

        do i=1,3
           w(i)=v(i)-u(i)
        end do 
        return
        end

        subroutine addvect(v,u,w)
c vector w = v+u
        real v(3),u(3),w(3)
        integer i

        do i=1,3
           w(i)=v(i)+u(i)
        end do
        return
        end


        subroutine mul(a,v,w) 
c vector w = av    where a is a real constant
        real a,v(3),w(3)
        integer i

        do i=1,3
           w(i)=a*v(i)
        end do
        return
        end

