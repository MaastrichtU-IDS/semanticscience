	subroutine wrt(ipgn)
	character*24 day
        character*24 fdate
        external fdate

c subroutine to handle log file writes
c
	if(ipgn.eq.1) then
	write(6,*)'   '
	write(6,*)' __________DelPhi V. 4 Release 1.1 ______________  '
	write(6,*)'|                                                | '
	write(6,*)'| A program to solve the PB equation             | '
	write(6,*)'| in 3D, using non-linear form, incorporating    | '
	write(6,*)'| many dielectric regions, multisalt ionic       | '
        write(6,*)'| strength, different probe radii, periodic      | '
	write(6,*)'| and focussing boundary conditions, utilizing   | '
	write(6,*)'| stripped optimum successive over-relaxation    | '
	write(6,*)'| and an improved algorithm for mapping the      | '
	write(6,*)'| Mol. Surface to the finite-Difference grid     | '
	write(6,*)'| Recompiled on Linux and PC                     | '
        write(6,*)'|    January 2002 --------  Walter Rocchia       | '
	write(6,*)'|__________________           ___________________| '
	write(6,*)'                   DelPhi V. 4                     '
	write(6,*)'  '
	day=fdate()
        write(6,*)' program started on ',day(1:10)//day(20:24)
        write(6,*)'             at ',day(12:19)
	end if
c
	return
	end
