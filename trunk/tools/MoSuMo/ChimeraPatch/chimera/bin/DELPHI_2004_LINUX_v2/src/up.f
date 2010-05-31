c------------------------------------------------------------
      subroutine up(txt,len)
c
c convert character string to upper case
c
      character*(*) txt
      character*80 save
      character*26 ualpha,lalpha
      data ualpha /'ABCDEFGHIJKLMNOPQRSTUVWXYZ'/
      data lalpha /'abcdefghijklmnopqrstuvwxyz'/

      do 9000 i=1,len
        if((txt(i:i).ge.'a').and.(txt(i:i).le.'z')) then
          match = index(lalpha,txt(i:i))
          save(i:i) = ualpha(match:match)
        else
          save(i:i) = txt(i:i)
        end if
c      end do
9000	continue

      txt = save
      return
      end

