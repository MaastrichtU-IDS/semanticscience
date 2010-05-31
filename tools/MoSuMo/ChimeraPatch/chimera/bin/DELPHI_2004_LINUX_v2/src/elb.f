c----------------------------------------------------------
      subroutine elb(txt,len)
c
c eliminate leading blanks from a character string
c
      character*(*) txt
      character*80 save

      do 9000 i=1,len
        if(txt(i:i).ne.' ') then
          nonb = i
          go to 100
        end if
9000  continue
      return
100   continue
      save = txt(nonb:len)
      txt = save
      return
      end
