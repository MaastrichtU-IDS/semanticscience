#ifndef otf_molkit_MolComment_h
# define otf_molkit_MolComment_h

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

// $Id: MolComment.h 26655 2009-01-07 22:02:30Z gregc $

# include "TimeStamp.h"

namespace otf {

class OTF_IMEX MolComment {
	Symbol		_tag;
	TimeStamp	ts;
	std::string	comment;
public:
		MolComment(Symbol tag, const TimeStamp &whoWhen,
						const std::string &text):
			_tag(tag), ts(whoWhen), comment(text) {}
		MolComment(Symbol tag, const char *who, const std::string &text):
			_tag(tag), ts(time(NULL), who), comment(text) {}
	Symbol	tag() const { return _tag; }
	const TimeStamp &
		timeStamp() const { return ts; }
	const std::string &
		text() const { return comment; }
};

} // namespace otf

#endif
