#ifndef otf_dirent_h
# define otf_dirent_h

# include "config.h"

# if !defined(_WIN32)
#  include <dirent.h>
# else
#  include "win32_dirent.h"
# endif

#endif
