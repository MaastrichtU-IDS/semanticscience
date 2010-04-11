	subroutine wrtvisual(natom,igrid,nobject,scale,oldmid,nmedia,epkt)
c+++++++++++added by walter 10 Aug 1999
c writes down a text file that contains geometrical data for
c the connection with the GUI
c
        include 'pointer.h'

        integer nmedia,natom,nobject,ii,objecttype,ix,igrid,imedia
        real color
        integer iatmmed(natom+nobject)
	real xn2(3,natom),rad3(natom),chrgv4(natom)
        character*80 dataobject(nobject,2)
        character*80 strtmp
        real side,xa(3),xb(3),xc(3),xd(3)
        real tmpvect(3),modul2,tmp,tmp1,oldmid(3),radius,rmid
        real pi,tmpvect1(3),zero,epkt,alpha
        real medeps(0:nmedia),repsin,scale
  
         
        pi=3.1416
        zero=0.0
        rmid=float((igrid+1)/2)
        open(52,FILE='visual.txt')
c       write(52,*)igrid,'  //grid points on a side cube'
        write(52,'(I3.3)')igrid
c       side = side of the box in Amstrong
        side=(igrid-1)/scale
c       write(52,*)side,'  //actual lenght of the side cube,(Amstrong)'
        write(52,100)side
100     format (sp,e12.5)
200     format (sp,e12.5)

c       here we have the X-axis
        objecttype=9
        color=0.0
        write(52,'(I3.3)')objecttype
        write(52,200)color
        write(52,100) float(igrid-1)
        write(52,100) -pi/2
        write(52,100) zero
        write(52,100)zero
        write(52,100)(-oldmid(1))*scale+rmid
        write(52,100)(-oldmid(2))*scale+rmid
        write(52,100)(-oldmid(3))*scale+rmid
c       here we have the Y-axis
        objecttype=9
        color=0.5
        write(52,'(I3.3)')objecttype
        write(52,200)color
        write(52,100) float(igrid-1)
        write(52,100) -pi/2
        write(52,100) -pi/2
        write(52,100) -pi/2
        write(52,100)(-oldmid(1))*scale+rmid
        write(52,100)(-oldmid(2))*scale+rmid
        write(52,100)(-oldmid(3))*scale+rmid
c       here we have the Z-axis
        objecttype=9
        color=1.
        write(52,'(I3.3)')objecttype
        write(52,200)color
        write(52,100) float(igrid-1)
        write(52,100) -pi/2
        write(52,100) -pi/2
        write(52,100)zero   
        write(52,100)(-oldmid(1))*scale+rmid
        write(52,100)(-oldmid(2))*scale+rmid
        write(52,100)(-oldmid(3))*scale+rmid

        do ii=1,nobject
        imedia=iatmmed(natom+ii)
        repsin=medeps(imedia)*epkt
        color=250*(1-exp((repsin-1)/80))/255
        strtmp=dataobject(ii,1)
        if ((strtmp(1:4).ne.'is a')) then
           read(strtmp(8:10),'(I3)')objecttype
           if (objecttype.eq.1) then
c              here we have a sphere
c              write(52,*)objecttype,'  //sphere'
               write(52,'(I3.3)')objecttype
               write(52,200)color
               read(strtmp(20:80),*)xb,radius
               tmp=radius*scale
               write(52,100)tmp
               tmp=(xb(1)-oldmid(1))*scale+rmid
               write(52,100)tmp
               tmp=(xb(2)-oldmid(2))*scale+rmid
               write(52,100)tmp
               tmp=(xb(3)-oldmid(3))*scale+rmid
               write(52,100)tmp
           end if

           if (objecttype.eq.2) then
c              here we have a cylinder
               write(52,'(I3.3)')objecttype
               write(52,200)color
               read(strtmp(20:80),*)xa,xb,radius
               call diffvect(xa,xb,tmpvect)
               call inner(tmpvect,tmpvect,modul2)
               tmp=radius*scale
               write(52,100)tmp
               tmp=sqrt(modul2)*scale
               write(52,100)tmp
c iniziano gli angoli di rotazione
               write(52,100) -pi/2
               call mul(scale/tmp,tmpvect,tmpvect)
               tmp=-acos(tmpvect(1))
               write(52,100)tmp
               if (abs(tmpvect(1)**2-1).lt.1.0e-8)then
                  tmp=zero                      
               else
                  tmp=-asin(tmpvect(2)/sqrt(1-tmpvect(1)**2))
               end if
               write(52,100)tmp
c              find middle point
               call addvect(xa,xb,tmpvect)
               call mul(0.5,tmpvect,tmpvect)
               tmp=(tmpvect(1)-oldmid(1))*scale+rmid
               write(52,100)tmp
               tmp=(tmpvect(2)-oldmid(2))*scale+rmid
               write(52,100)tmp
               tmp=(tmpvect(3)-oldmid(3))*scale+rmid
               write(52,100)tmp
           end if

           if (objecttype.eq.3) then
c             here we have a cone
              write(52,'(I3.3)')objecttype
              write(52,200)color
              read(strtmp(20:80),*)xa,xb,alpha
c             xa=coordinates of the tip
c             alpha is expressed in degrees, so it needs a conversion
              alpha=alpha*3.1415/180.
              call diffvect(xa,xb,tmpvect)
              call inner(tmpvect,tmpvect,modul2)
              tmp=sqrt(modul2)*scale
              tmp1=tmp*tan(alpha)
              write(52,100)tmp1
              write(52,100)tmp
c iniziano gli angoli di rotazione
              write(52,100) -pi/2
              call mul(scale/tmp,tmpvect,tmpvect)
              tmp=-acos(tmpvect(1))
              write(52,100)tmp
              if (abs(tmpvect(1)**2-1).lt.1.0e-8)then
                 tmp=zero
              else
                 tmp=-asin(tmpvect(2)/sqrt(1-tmpvect(1)**2))
              end if
              write(52,100)tmp

c             find middle point
              call addvect(xa,xb,tmpvect)
              call mul(0.5,tmpvect,tmpvect)
              tmp=(tmpvect(1)-oldmid(1))*scale+rmid
              write(52,100)tmp
              tmp=(tmpvect(2)-oldmid(2))*scale+rmid
              write(52,100)tmp
              tmp=(tmpvect(3)-oldmid(3))*scale+rmid
              write(52,100)tmp
           end if

           if (objecttype.eq.4) then
c             here we have a box
              write(52,'(I3.3)')objecttype
              write(52,200)color

              read(strtmp(20:80),*)xa,xb,xc,xd
              call diffvect(xb,xa,tmpvect)
              call inner(tmpvect,tmpvect,modul2)
              tmp=sqrt(modul2)*scale
              write(52,100)tmp/2

              call diffvect(xc,xa,tmpvect1)
              call inner(tmpvect1,tmpvect1,modul2)
              tmp=sqrt(modul2)*scale
              call mul(scale/tmp,tmpvect1,tmpvect1)
              write(52,100)tmp/2

              call diffvect(xd,xa,tmpvect)
              call inner(tmpvect,tmpvect,modul2)
              tmp=sqrt(modul2)*scale
              call mul(scale/tmp,tmpvect,tmpvect)
              write(52,100)tmp/2

c             no conversion to axial symmetry points

              if (abs(tmpvect(1)**2-1.).lt.1.0e-8) then
                 tmp=asin(tmpvect1(3)/tmpvect(1))
                 if (tmpvect1(2).lt.0.0) tmp=pi-tmp
              else
                 tmp=-asin(tmpvect1(1)/sqrt(1-tmpvect(1)**2))
                 if ((tmpvect(3)*tmpvect1(2)-tmpvect(2)*tmpvect1(3))
     &  .lt.0.0) tmp=pi-tmp
              end if 
              write(52,100)tmp

              tmp=asin(tmpvect(1))
              write(52,100)tmp
              if (abs(tmpvect(3)).lt.1.0e-8)then
                 tmp=-sign(pi/2.,tmpvect(2))
                 if (abs(tmpvect(2)).lt.1.0e-8)tmp=0.0
              else
                  tmp=-atan(tmpvect(2)/tmpvect(3))
                  if (tmpvect(3).lt.0.0) tmp=tmp+pi
              end if
              write(52,100)tmp

c             find middle point
              call addvect(xa,xb,tmpvect)
              call addvect(tmpvect,xc,tmpvect)
              call addvect(tmpvect,xd,tmpvect)
              call mul(0.5,tmpvect,tmpvect)
              tmp=(tmpvect(1)-oldmid(1))*scale+rmid
              write(52,100)tmp
              tmp=(tmpvect(2)-oldmid(2))*scale+rmid
              write(52,100)tmp
              tmp=(tmpvect(3)-oldmid(3))*scale+rmid
              write(52,100)tmp

           end if
c NOTE that the following objecttypes are fictious

           if (objecttype.eq.8) then
c              here we have a point
               write(52,'(I3.3)')objecttype
               write(52,200)color
               read(strtmp(20:80),*)xb
               tmp=(xb(1)-oldmid(1))*scale+rmid
               write(52,100)tmp
               tmp=(xb(2)-oldmid(2))*scale+rmid
               write(52,100)tmp
               tmp=(xb(3)-oldmid(3))*scale+rmid
               write(52,100)tmp
           end if

           if (objecttype.eq.9) then
c              here we have a line
               write(52,'(I3.3)')objecttype
               write(52,200)color
               read(strtmp(20:80),*)xa,xb
               call diffvect(xa,xb,tmpvect)
               call inner(tmpvect,tmpvect,modul2)
               tmp=sqrt(modul2)*scale
               write(52,100)tmp
c iniziano gli angoli di rotazione
              write(52,100) -pi/2
              call mul(scale/tmp,tmpvect,tmpvect)
              tmp=-acos(tmpvect(1))
              write(52,100)tmp
              if (abs(tmpvect(1)**2-1).lt.1.0e-8)then
                 tmp=zero
              else
                 tmp=-asin(tmpvect(2)/sqrt(1-tmpvect(1)**2))
              end if
              write(52,100)tmp

c              find middle point
               call addvect(xa,xb,tmpvect)
               call mul(0.5,tmpvect,tmpvect)
               tmp=(tmpvect(1)-oldmid(1))*scale+rmid
               write(52,100)tmp
               tmp=(tmpvect(2)-oldmid(2))*scale+rmid
               write(52,100)tmp
               tmp=(tmpvect(3)-oldmid(3))*scale+rmid
               write(52,100)tmp
           end if

           if (objecttype.eq.10) then
c              here we have a disk
               write(52,'(I3.3)')objecttype
               write(52,200)color
               read(strtmp(20:80),*)xa,xb,radius
               call diffvect(xa,xb,tmpvect)
               tmp=radius*scale
               write(52,100)tmp
c iniziano gli angoli di rotazione
              write(52,100) -pi/2
              call mul(scale/tmp,tmpvect,tmpvect)
              tmp=-acos(tmpvect(1))
              write(52,100)tmp
              if (abs(tmpvect(1)**2-1).lt.1.0e-8)then
                 tmp=zero
              else
                 tmp=-asin(tmpvect(2)/sqrt(1-tmpvect(1)**2))
              end if
              write(52,100)tmp

               tmp=(xb(1)-oldmid(1))*scale+rmid
               write(52,100)tmp
               tmp=(xb(2)-oldmid(2))*scale+rmid
               write(52,100)tmp
               tmp=(xb(3)-oldmid(3))*scale+rmid
               write(52,100)tmp
           end if

        else
c now we deal with a molecule
           write(52,'(I1.1)')int(zero)
           write(52,'(I5.5)')natom
           do 2103 ix=1,natom
              tmp=rad3(ix)*scale
              write(52,100)tmp
              write(52,100)chrgv4(ix)
              write(52,100)xn2(1,ix)
              write(52,100)xn2(2,ix)
              write(52,100)xn2(3,ix)
2103       continue

        end if
        end do

        close(52)
999	continue
	return
	end
