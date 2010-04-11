// vi:set ts=4 sw=4:
// --- UCSF Chimera Copyright ---
// Copyright (c) 2000 Regents of the University of California.
// All rights reserved.  This software provided pursuant to a
// license agreement containing restrictions on its disclosure,
// duplication and use.  This notice must be embedded in or
// attached to all copies, including partial copies, of the
// software or any revisions or derivations thereof.
// --- UCSF Chimera Copyright ---
//
// $Id: VrmlNodeType.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef VRML_NODETYPE
#define	VRML_NODETYPE
/**************************************************
 * VRML 2.0 Parser
 * Copyright (C) 1996 Silicon Graphics, Inc.
 *
 * Author(s)	: Gavin Bell
 *				Daniel Woods (first port)
 **************************************************
 */

//
// The VrmlNodeType class is responsible for storing information about node
// or prototype types.
//

#include "common.h"
#include "RefCount.h"
#include "RefCount.h"
#include <vector>

namespace VRML {

class Node;
class Field;

class VrmlNodeType : public RefCount {
  public:
  	// Constructor.  Takes name of new type (e.g. "Transform" or "Box")
	// Copies the string given as name.
	VrmlNodeType(const char *nm);

	// Destructor exists mainly to deallocate storage for name
	~VrmlNodeType();

	// Namespace management functions.  PROTO definitions add node types
	// to the namespace.  PROTO implementations are a separate node
	// namespace, and require that any nested PROTOs NOT be available
	// outside the PROTO implementation.
	// addToNameSpace will print an error to stderr if the given type
	// is already defined.
	static void addToNameSpace(VrmlNodeType *);
	static void pushNameSpace();
	static void popNameSpace();

	// Find a node type, given its name.  Returns NULL if type is not defined.
	static VrmlNodeType *find(const char *nm);

	// Routines for adding/getting eventIns/Outs/fields
	void addEventIn(const char *name, int type, Field *field);
	void addEventOut(const char *name, int type, Field *field);
	void addField(const char *name, int type, Field *field);
	void addExposedField(const char *name, int type, Field *field);

	int hasEventIn(const char *name) const;
	int hasEventOut(const char *name) const;
	int hasField(const char *name) const;
	int hasExposedField(const char *name) const;

	Field *fieldWithName(const char *name) const;

	// Routines for adding nodes during declaration and
	// expanding nodes when applying proto
	void addNode(Node *node);
	const std::vector<Node *> &nodeList() const { return nodes; }
	bool isPrimitive() const { return nodes.size() == 0; }
	
	const char *getName() const { return name; }
	void print(std::ostream &s, int indent) const;

	typedef struct {
		char *name;
		int type;
		Field *field;
	} NameTypeRec;
		
  private:
	void add(std::vector<NameTypeRec*> &,const char *,int,Field *);
	int has(const std::vector<NameTypeRec*> &,const char *) const;
	void printDecl(std::ostream &s, int indent, const char *prefix,
						const std::vector<NameTypeRec*> &) const;

	char *name;

	// Node types are stored in this data structure:
	static std::vector<VrmlNodeType*> typeList;

	std::vector<NameTypeRec*> eventIns;
	std::vector<NameTypeRec*> eventOuts;
	std::vector<NameTypeRec*> fields;
	std::vector<Node *> nodes;
};

} // namespace VRML

#endif
