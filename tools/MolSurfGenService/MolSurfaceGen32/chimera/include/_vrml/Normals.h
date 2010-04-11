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
// $Id: Normals.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef VRML_NORMALS
#define	VRML_NORMALS

#include "common.h"
#include "Field.h"
#include "Matrix.h"

#include <map>
#include <functional>

namespace VRML {

class Edge {
protected:
	int			v1_, v2_;
	int			nPoly_;
	int			polygon_[2];
public:
				Edge();
				Edge(int v1, int v2);
	void		addPolygon(int offset);
	int			polygonCount() const	{ return nPoly_; }
	const int	*polygons() const	{ return polygon_; }
	bool		operator==(const Edge &other) const;
	bool		operator<(const Edge &other) const;
};

typedef std::pair<int, int>			IntPair;
typedef std::map<IntPair, Edge, std::less<IntPair> >		VertexEdgeMap;
typedef std::map<int, Vector, std::less<int> >	PolygonNormalMap;

typedef std::pair<MFInt32 *, MFVec3F *>	IndexNormalPair;

extern IndexNormalPair	generateFaceNormals(const MFInt32 &coordIndex,
												const MFVec3F &coord,
												bool ccw, float creaseAngle);

} // namespace VRML

#endif
