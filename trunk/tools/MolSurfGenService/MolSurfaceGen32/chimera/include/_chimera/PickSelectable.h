#ifndef Chimera_PickSelectable_h
# define Chimera_PickSelectable_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include "_chimera_config.h"

namespace chimera {

class Selectable;

inline void
setPickSelectable(const Selectable *s)
{
# ifndef CHIMERA_64BITPTR
	glLoadName(reinterpret_cast<GLuint>(s));
# else
	unsigned long name = reinterpret_cast<unsigned long>(s);
	glLoadName(name & 0xffffffff);
	glPushName(name >> 32);
# endif
}

inline void
clearPickSelectable()
{
# ifdef CHIMERA_64BITPTR
	glPopName();
# endif
}

} // namespace chimera

#endif
