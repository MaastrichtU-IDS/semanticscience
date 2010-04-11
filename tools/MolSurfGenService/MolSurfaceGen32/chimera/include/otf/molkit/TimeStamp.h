#ifndef otf_molkit_TimeStamp_h
# define otf_molkit_TimeStamp_h

// Copyright (c) 1996 The Regents of the University of California.
// All rights reserved.
// 
// Redistribution and use in source and binary forms are permitted
// provided that the above copyright notice and this paragraph are
// duplicated in all such forms and that any documentation,
// distribution and/or use acknowledge that the software was developed
// by the Computer Graphics Laboratory, University of California,
// San Francisco.  The name of the University may not be used to
// endorse or promote products derived from this software without
// specific prior written permission.
// 
// THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
// WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
// IN NO EVENT SHALL THE REGENTS OF THE UNIVERSITY OF CALIFORNIA BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
// OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF THIS SOFTWARE.

// $Id: TimeStamp.h 26655 2009-01-07 22:02:30Z gregc $

# include <otf/Symbol.h>
# include <time.h>

# ifdef __BORLANDC__
	// not sure why this happens
	using std::time_t;
	using std::ctime;
# endif

namespace otf {

class OTF_IMEX TimeStamp {
	time_t	date;
	Symbol	user;
public:
		TimeStamp(time_t t, const char *who): date(t), user(who) {}
		TimeStamp(time_t t, const std::string &who): date(t), user(who) {}
		TimeStamp(time_t t, Symbol who): date(t), user(who) {}
	Symbol	who() const { return user; }
	time_t	when() const { return date; }
	bool		operator==(const TimeStamp &ts) const;
	bool		operator!=(const TimeStamp &ts) const;
	bool		operator<(const TimeStamp &ts) const;
	bool		operator<=(const TimeStamp &ts) const;
	bool		operator>(const TimeStamp &ts) const;
	bool		operator>=(const TimeStamp &ts) const;
	std::string	str() const;
};

inline std::ostream &
operator<<(std::ostream &os, const TimeStamp &ts)
{
	os << ts.str();
	return os;
}

} // namespace otf

#endif
