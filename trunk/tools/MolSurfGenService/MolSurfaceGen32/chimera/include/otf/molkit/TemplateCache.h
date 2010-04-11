#ifndef otf_molkit_TemplateCache_h
#define otf_molkit_TemplateCache_h

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

#include <otf/Symbol.h>
#include <vector>
#include <utility>
#include <map>

namespace otf {
	
class OTF_IMEX CondInfo {
public:
	otf::Symbol op, operand, result;
	CondInfo(otf::Symbol o1, otf::Symbol o2, otf::Symbol res) :
					op(o1), operand(o2), result(res) {}
};

class OTF_IMEX ConditionalTemplate {
public:
	std::vector<CondInfo> conditions;
	void addCondition(const char *cond, const char *type);
};

class OTF_IMEX TemplateCache {
public:
	typedef std::pair<std::string, ConditionalTemplate *> AtomMappings;
		// <normal IDATM type, conditional IDATM types>
	typedef std::map<std::string, AtomMappings> AtomMap;
		// atom name -> AtomMappings
	typedef std::map<otf::Symbol, AtomMap> ResMap;
		// res name -> AtomMap
	AtomMap *resTemplate(otf::Symbol resType, const char *app,
			const char *templateDir, const char *extension);
	virtual ~TemplateCache();
	static TemplateCache *templateCache();
protected:
	TemplateCache() {};
private:
	std::map<std::string, ResMap> cache;
		// searchpath/extension -> resMap
	void cacheTemplateType(std::string &key, const char *app,
			const char *templateDir, const char *extension);
	AtomMap parseTemplateFile(std::ifstream &, std::string &);
	static TemplateCache *_instance;
};

} // namespace otf

#endif
