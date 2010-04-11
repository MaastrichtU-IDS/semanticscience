        subroutine datime(day)
   
        character*24 day
        character*24 fdate
        external fdate

        day=fdate()

        end

        subroutine ddtime(tarray)
  
        real tarray(2)
        real dtime
        external dtime

        sum=dtime(tarray)

        end

        subroutine eetime(tarray)
 
        real tarray(2)
        real etime
        external etime

        sum=etime(tarray)

        end

