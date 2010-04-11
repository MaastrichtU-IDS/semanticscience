/*
 * Copyright (c) 1992-1996 The Regents of the University of California.
 * All rights reserved.
 * 
 * Redistribution and use in source and binary forms are permitted
 * provided that the above copyright notice and this paragraph are
 * duplicated in all such forms and that any documentation,
 * distribution and/or use acknowledge that the software was developed
 * by the Computer Graphics Laboratory, University of California,
 * San Francisco.  The name of the University may not be used to
 * endorse or promote products derived from this software without
 * specific prior written permission.
 * 
 * THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
 * IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
 * WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
 * IN NO EVENT SHALL THE REGENTS OF THE UNIVERSITY OF CALIFORNIA BE
 * LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 * OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF THIS SOFTWARE.
 *
 * $Id: PDB.h 27484 2009-05-04 21:59:56Z gregc $
 *
 * Based on Brookhaven National Laboratory Protein Data Bank Format 2.0
 *
 * C structure declarations
 */

#ifndef PDB_H
# define	PDB_H

# ifdef __cplusplus
#  include <iostream>
# else
#  include <stdio.h>
# endif
#ifndef OTF_IMEX
# include <otf/config.h>
#endif

# ifdef __cplusplus
namespace otf {

class OTF_IMEX PDB {
public:
# endif

# if !defined(__cplusplus) || defined(OTF_USE_ENUM)
	enum { BufLen = 82, PDBRUNVersion = 6 };
# else
	static const int BufLen = 82;		// PDB record length (80 + "\n")
	static const int PDBRUNVersion = 6;	// Best version generated
# endif
	/*
	 * These types are from PDB 2.0 Appendix 6.
	 * The types that map to C types or types that map to character
	 *	arrays of varying lengths are not duplicated.
	 */
	typedef char	Atom[5];
	typedef char	Date[10];
	typedef char	IDcode[5];
	typedef double	Real;
	typedef char	ResidueName[5];		/* local extension */

	/* our constructed type */
	struct Residue {
		ResidueName	name;
		char	chainID;
		int	seqNum;
		char	iCode;
	};
# ifndef __cplusplus
	typedef struct Residue Residue;
# endif

	/* graphics primitive types */
	enum GfxType {
		GFX_UNKNOWN, GFX_POINTS, GFX_MARKERS, GFX_LINES,
		GFX_LINE_STRIP, GFX_LINE_LOOP, GFX_TRIANGLES,
		GFX_TRIANGLE_STRIP, GFX_TRIANGLE_FAN, GFX_QUADS,
		GFX_QUAD_STRIP, GFX_POLYGON
	};

	/*
	 *	structures declarations for each record type
	 */

	typedef struct {
		char	junk[BufLen];
	} Unknown_;
	typedef struct {
		int	serial;
		Atom	name;
		char	altLoc;
		Residue	res;
		int	u[6];
		char	segID[5];
		char	element[3];
		char	charge[3];
	} Anisou_;
	typedef struct {
		int	serial;
		Atom	name;
		char	altLoc;
		Residue	res;
		Real	xyz[3];
		Real	occupancy, tempFactor;
		char	segID[5];
		char	element[3];
		char	charge[3];
	} Atom_;
	typedef struct {
		int	continuation;
		char	authorList[71];
	} Author_;
	typedef struct {
		int	continuation;
		IDcode	idCode;
		char	comment[62];
	} Caveat_;
	typedef struct {
		int	serNum;
		Residue	pep[2];
		int	modNum;
		Real	measure;
	} Cispep_;
	typedef struct {
		int	continuation;
		char	compound[61];
	} Compnd_;
	typedef struct {
		int	serial[11];
	} Conect_;
	typedef struct {
		Real	a, b, c;
		Real	alpha, beta, gamma;
		char	sGroup[12];
		int	z;
	} Cryst1_;
	typedef struct {
		IDcode	idCode;
		char	chainID;
		int	seqBegin;
		char	insertBegin;
		int	seqEnd;
		char	insertEnd;
		char	database[7];
		char	dbAccession[9];
		char	dbIdCode[13];
		int	seqBegin2;
		char	insBegpdb;
		int	seqEnd2;
		char	insEndpdb;
	} Dbref_;
	typedef struct {
		IDcode	idCode;
		char	chainID;
		int	seqBegin;
		char	insertBegin;
		int	seqEnd;
		char	insertEnd;
		char	database[7];
		char	dbIdCode[21];
	} Dbref1_;
	typedef struct {
		IDcode	idCode;
		char	chainID;
		char	dbAccession[23];
		int	seqBegin;
		int	seqEnd;
	} Dbref2_;
	/* no structure for END */
	/* no structure for ENDMDL */
	typedef struct {
		int	continuation;
		char	technique[61];
	} Expdta_;
	typedef struct {
		int	compNum;
		ResidueName	hetID;
		int	continuation;
		char	exclude;	/* '*' to exclude */
		char	formula[52];
	} Formul_;
	typedef struct {		/* removed in PDB Version 2.0 */
		char	num[4];
		char	text[70];
	} Ftnote_;
	typedef struct {
		char	classification[41];
		Date	depDate;
		IDcode	idCode;
	} Header_;
	typedef struct {
		int	serNum;
		char	helixID[4];
		Residue	init;
		Residue	end;
		int	helixClass;
		char	comment[31];
		int	length;
	} Helix_;
	typedef struct {
		Residue	res;
		int	numHetAtoms;
		char	text[51];
	} Het_;
	typedef Atom_	Hetatm_;
	typedef struct {
		int	continuation;
		ResidueName	hetID;
		char	name[66];
	} Hetnam_;
	typedef struct {
		int	continuation;
		ResidueName	hetID;
		char	synonyms[66];
	} Hetsyn_;
	typedef struct {
		/* 0 = atom 1, 1 = atom 2, 2 = hydrogen atom */
		Atom	name[3];
		char	altLoc[3];
		Residue	res[3];
		int	sym[2];
	} Hydbnd_;
	typedef struct {
		int	continuation;
		char	text[59];
	} Jrnl_;
	typedef struct {
		int	continuation;
		char	keywds[71];
	} Keywds_;
	typedef struct {
		Atom	name[2];
		char	altLoc[2];
		Residue	res[2];
		int	sym[2];
		Real	length;
	} Link_;
	typedef struct {
		int	numRemark;
		int	numFtnote;
		int	numHet;
		int	numHelix;
		int	numSheet;
		int	numTurn;
		int	numSite;
		int	numXform;
		int	numCoord;
		int	numTer;
		int	numConect;
		int	numSeq;
	} Master_;
	typedef struct {
		int	continuation;
		char	comment[71];
	} Mdltyp_;
	typedef struct {
		int	serial;
	} Model_;
	typedef struct {
		IDcode	idCode;
		Residue	res;
		ResidueName	stdRes;
		char	comment[52];
	} Modres_;
	/* Mtrix_ is for MTRIX1, MTRIX2, and MTRIX3 */
	typedef struct {
		int	rowNum;
		int	serial;
		Real	m[3], v;
		int	iGiven;
	} Mtrix_;
	typedef struct {
		int	modelNumber;
	} Nummdl_;
	typedef struct {
		int	continuation;
		Date	repDate;
		IDcode	idCode;
		IDcode	rIdCode[8];
	} Obslte_;
	/* Origx_ is for ORIGX1, ORIGX2, and ORIGX3 */
	typedef struct {
		int	rowNum;
		Real	o[3], t;
	} Origx_;
	typedef struct {
		int	remarkNum;
		char	empty[70];
	} Remark_;
	typedef struct {
		int	modNum;
		int	continuation;
		Date	modDate;
		char	modId[6];
		int	modType;
		char	record[4][7];
	} Revdat_;
	/* Scale_ is for SCALE1, SCALE2, and SCALE3 */
	typedef struct {
		int	rowNum;
		Real	s[3], u;
	} Scale_;
	typedef struct {
		IDcode	idCode;
		Residue	res;
		char	database[5];
		char	dbIdCode[10];
		ResidueName	dbRes;
		int	dbSeq;
		char	conflict[32];
	} Seqadv_;
	typedef struct {
		int	serNum;
		char	chainID;
		int	numRes;
		ResidueName	resName[13];
	} Seqres_;
	typedef struct {
		int	strand;
		char	sheetID[4];
		int	numStrands;
		Residue	init;
		Residue	end;
		int	sense;
		Atom	curAtom;
		Residue	cur;
		Atom	prevAtom;
		Residue	prev;
	} Sheet_;
	typedef struct {
		int	serial;
		Atom	name;
		char	altLoc;
		Residue	res;
		Real	sigXYZ[3];
		Real	sigOcc, sigTemp;
		char	segID[5];
		char	element[3];
		char	charge[3];
	} Sigatm_;
	typedef struct {
		int	serial;
		Atom	name;
		char	altLoc;
		Residue	res;
		Real	sig[6];
		char	segID[5];
		char	element[3];
		char	charge[3];
	} Siguij_;
	typedef struct {
		int	seqNum;
		char	siteID[4];
		int	numRes;
		Residue	res[4];
	} Site_;
	typedef struct {
		Atom	name[2];
		char	altLoc[2];
		Residue	res[2];
		int	sym[2];
	} Sltbrg_;
	typedef struct {
		int	continuation;
		char	srcName[61];
	} Source_;
	typedef struct {
		int	continuation;
		IDcode	idCode[14];
	} Split_;
	typedef struct {
		int	continuation;
		Date	sprsdeDate;
		IDcode	idCode;
		IDcode	sIdCode[8];
	} Sprsde_;
	typedef struct {
		int	serNum;
		Residue	res[2];
		int	sym[2];
		Real	length;
	} Ssbond_;
	typedef struct {
		int	serial;
		Residue	res;
	} Ter_;
	typedef struct {
		int	continuation;
		char	title[61];
	} Title_;
	typedef struct {
		int	seq;
		char	turnID[4];
		Residue	init;
		Residue	end;
		char	comment[31];
	} Turn_;
	typedef struct {
		int	serial;
		Real	t[3];
		char	comment[31];
	} Tvect_;
	typedef struct {
		char	subtype[3];
		char	text[75];
	} User_;
	typedef struct {
		int	version;
	} UserPdbrun;
	typedef struct {
		Real	xyz[3];
	} UserEyePos;
	typedef UserEyePos UserAtPos;
	typedef struct {
		Real	left, right, bottom, top, hither, yon;
	} UserWindow;
	typedef struct {
		Real	focus;
	} UserFocus;
	typedef struct {
		Real	xmin, xmax, ymin, ymax;
	} UserViewport;
	typedef struct {
		Real	rgb[3];
	} UserBgColor;
	typedef struct {
		int	mol0, mol1, mol2, mol3;	/* new in version 7 */
		int	atom0, atom1, atom2, atom3;
		Real	angle;
		int	which;			/* version 5 -- obsolete */
	} UserAngle;
	typedef struct {
		int	mol0, mol1;		/* new in version 7 */
		int	atom0, atom1;
		Real	distance;
		int	which;			/* version 5 -- obsolete */
	} UserDistance;
	typedef struct {
		char	filename[62];
		int	model;			/* not in version 5 */
	} UserFile;
	typedef struct {			/* not in version 5 */
		char	markname[58];
	} UserMarkname;
	typedef UserMarkname UserMark;		/* not in version 5 */
	typedef struct {
		Real	rgb[3];
		char	name[39];
	} UserCName;
	typedef struct {
		Real	rgb[3];
		char	spec[39];
	} UserColor;
	typedef struct {
		Real	radius;
	} UserRadius;
	typedef struct {
		int	model;			/* version 5 -- obsolete */
	} UserObject;
	typedef struct {
		int	model;			/* version 5 -- obsolete */
	} UserEndObj;
	typedef struct {
		int	atom0, atom1;
	} UserChain;
	typedef struct {			/* not in version 5 */
# ifndef __cplusplus
		enum
# endif
		GfxType	primitive;
		char	unknown[33];
	} UserGfxBegin;
	/* no structure for USER  GFX END */
	typedef UserColor UserGfxColor;
	typedef struct {			/* not in version 5 */
		Real	xyz[3];
	} UserGfxNormal;
	typedef UserGfxNormal UserGfxVertex;
	typedef struct {
		int	size;
		char	name[54];
	} UserGfxFont;
	typedef struct {			/* not in version 5 */
		Real	xyz[3];
	} UserGfxTextPos;
	typedef struct {
		Real	xyz[3];			/* version 5 -- obsolete */
		char	text[57];		/* 27 in version 5 */
	} UserGfxLabel;
	typedef struct {			/* version 5 -- obsolete */
		Real	xyz[3];
	} UserGfxMove;
	typedef UserGfxMove UserGfxDraw;	/* version 5 -- obsolete */
	typedef UserGfxMove UserGfxMarker;	/* version 5 -- obsolete */
	typedef UserGfxMove UserGfxPoint;	/* version 5 -- obsolete */

	enum RecordType { UNKNOWN,
		ANISOU, ATOM, ATOM1, ATOM2, ATOM3, ATOM4, ATOM5, ATOM6, ATOM7,
		ATOM8, ATOM9, AUTHOR,
		CAVEAT, CISPEP, COMPND, CONECT, CRYST1,
		DBREF, DBREF1, DBREF2, END, ENDMDL, EXPDTA, FORMUL, FTNOTE,
		HEADER, HELIX, HET, HETATM, HETNAM, HETSYN, HYDBND,
		JRNL, KEYWDS, LINK,
		MASTER, MDLTYP, MODEL, MODRES, MTRIX, NUMMDL,
		OBSLTE, ORIGX, REMARK, REVDAT,
		SCALE, SEQADV, SEQRES, SHEET, SIGATM, SIGUIJ, SITE, SLTBRG,
		SOURCE, SPLIT, SPRSDE, SSBOND,
		TER, TITLE, TURN, TVECT,
		USER,
		USER_PDBRUN, USER_EYEPOS, USER_ATPOS, USER_WINDOW, USER_FOCUS,
		USER_VIEWPORT, USER_BGCOLOR, USER_ANGLE, USER_DISTANCE,
		USER_FILE, USER_MARKNAME, USER_MARK, USER_CNAME, USER_COLOR,
		USER_RADIUS, USER_OBJECT, USER_ENDOBJ, USER_CHAIN,
		USER_GFX_BEGIN, USER_GFX_END, USER_GFX_COLOR, USER_GFX_NORMAL,
		USER_GFX_VERTEX, USER_GFX_FONT, USER_GFX_TEXTPOS,
		USER_GFX_LABEL,
		USER_GFX_MOVE, USER_GFX_DRAW, USER_GFX_MARKER, USER_GFX_POINT
	};
# ifndef __cplusplus
#  define	PDB_NUM_R	(EXPDTA + 1)
#  define	PDB_NUM_USER_R	(USER_GFX_POINT - USER_PDBRUN + 1)
#  define	PDB_NUM_ALL_R	(USER_GFX_POINT + 1)
# elif defined(OTF_USE_ENUM)
	enum {
		NUM_TYPES = EXPDTA + 1,
		NUM_USER = USER_GFX_POINT - USER_PDBRUN + 1,
		NUM_ALL_TYPES = USER_GFX_POINT + 1
	};
# else
	static const int	NUM_TYPES = EXPDTA + 1;
	static const int	NUM_USER = USER_GFX_POINT - USER_PDBRUN + 1;
	static const int	NUM_ALL_TYPES = USER_GFX_POINT + 1;
# endif

# ifdef __cplusplus
private:
	RecordType	rType;
public:
#else
struct OTF_IMEX PDB { /*}*/
	enum RecordType	record_type;
# endif
	union {
		Unknown_	unknown;
		Anisou_	anisou;
		Atom_	atom;
		Author_	author;
		Caveat_	caveat;
		Cispep_	cispep;
		Compnd_	compnd;
		Conect_	conect;
		Cryst1_	cryst1;
		/* no End_ structure */
		/* no Endmdl_ structure */
		Dbref_	dbref;
		Dbref1_	dbref1;
		Dbref2_	dbref2;
		Expdta_	expdta;
		Formul_	formul;
		Ftnote_	ftnote;
		Header_	header;
		Helix_	helix;
		Het_	het;
		Hetatm_	hetatm;
		Hetnam_	hetnam;
		Hetsyn_	hetsyn;
		Hydbnd_	hydbnd;
		Jrnl_	jrnl;
		Keywds_	keywds;
		Link_	link;
		Master_	master;
		Mdltyp_	mdltyp;
		Model_	model;
		Modres_	modres;
		Mtrix_	mtrix;
		Nummdl_ nummdl;
		Obslte_	obslte;
		Origx_	origx;
		Remark_	remark;
		Revdat_	revdat;
		Scale_	scale;
		Seqres_	seqres;
		Seqadv_	seqadv;
		Sheet_	sheet;
		Sigatm_	sigatm;
		Siguij_	siguij;
		Site_	site;
		Sltbrg_	sltbrg;
		Source_	source;
		Split_	split;
		Sprsde_	sprsde;
		Ssbond_	ssbond;
		Ter_	ter;
		Title_	title;
		Turn_	turn;
		Tvect_	tvect;
		User_	user;
		UserPdbrun	userPdbrun;
		UserEyePos	userEyePos;
		UserAtPos	userAtPos;
		UserWindow	userWindow;
		UserFocus	userFocus;
		UserViewport	userViewport;
		UserBgColor	userBgColor;
		UserAngle	userAngle;
		UserDistance	userDistance;
		UserFile	userFile;
		UserMarkname	userMarkname;
		UserMark	userMark;
		UserCName	userCName;
		UserColor	userColor;
		UserRadius	userRadius;
		UserObject	userObject;
		UserEndObj	userEndObj;
		UserChain	userChain;
		UserGfxBegin	userGfxBegin;
		/* no UserGfxEnd structure */
		UserGfxColor	userGfxColor;
		UserGfxNormal	userGfxNormal;
		UserGfxVertex	userGfxVertex;
		UserGfxFont	userGfxFont;
		UserGfxTextPos	userGfxTextPos;
		UserGfxLabel	userGfxLabel;
		UserGfxMove	userGfxMove;
		UserGfxDraw	userGfxDraw;
		UserGfxMarker	userGfxMarker;
		UserGfxPoint	userGfxPoint;
	}
# ifndef __cplusplus
	pdb;		/* no anonymous unions in C */
# else
	;
private:
	static int	inputVersion;
	static int	pdbrunInputVersion;
	static int	pdbrunOutputVersion;
	static int	atomSerialNumber;
	static int	sigatmSerialNumber;
	static int	byteCmp(const PDB &l, const PDB &r);
public:

			PDB() { setType(UNKNOWN); }
			PDB(RecordType t) { setType(t); }
			PDB(const char *buf);
	RecordType	type() const { return rType; }
	void		setType(RecordType t);
	const char	*c_str() const;
	static int	PdbrunInputVersion() { return pdbrunInputVersion; }
	static int	PdbrunOutputVersion() { return pdbrunOutputVersion; }
	static void	setPdbrunInputVersion(int v) { pdbrunInputVersion = v; }
	static void	setPdbrunOutputVersion(int v) { pdbrunOutputVersion = v; }
	static RecordType
			getType(const char *buf);
	static GfxType	getGfxType(const char *buf);
	static const char
			*gfxChars(GfxType gt);
	static int	sscanf(const char *, const char *, ...);
	static int	sprintf(char *, const char *, ...);
	static void	resetState();

	inline bool operator==(const PDB &r) const {
				if (rType != r.rType)
					return 0;
				return byteCmp(*this, r) == 0;
			}
	inline bool operator!=(const PDB &r) const {
				if (rType != r.rType)
					return 1;
				return byteCmp(*this, r) != 0;
			}

	OTF_IMEX friend std::istream	&operator>>(std::istream &s, PDB &p);
# endif
};

# ifdef __cplusplus
inline std::ostream &
operator<<(std::ostream &s, const PDB &p)
{
	s << p.c_str();
	return s;
}

} // namespace otf

# else

typedef struct PDB PDB;

OTF_IMEX extern void	pdb_read_record(FILE *, PDB *);
OTF_IMEX extern void	pdb_read_string(const char *, PDB *);
OTF_IMEX extern void	pdb_write_record(FILE *, const PDB *);
OTF_IMEX extern void	pdb_write_string(char *, const PDB *);
OTF_IMEX extern void	pdb_reset_state(void);
# endif

#endif /* PDB_H */
