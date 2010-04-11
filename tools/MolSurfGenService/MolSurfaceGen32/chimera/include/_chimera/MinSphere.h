#ifndef WMLCONTMINSPHERE3_H
#define WMLCONTMINSPHERE3_H

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

#ifndef WrapPy

// Magic Software, Inc.
// http://www.magic-software.com
// http://www.wild-magic.com
// Copyright (c) 2004.  All Rights Reserved
//
// The Wild Magic Library (WML) source code is supplied under the terms of
// the license agreement http://www.magic-software.com/License/WildMagic.pdf
// and may not be copied or disclosed except in accordance with the terms of
// that agreement.

// Compute the minimum volume sphere containing the input set of points.  The
// algorithm randomly permutes the input points so that the construction
// occurs in 'expected' O(N) time.

#include <otf/Geom3d.h>
#include "_chimera_config.h"
#include <assert.h>

#define WML_ITEM CHIMERA_IMEX

//#include "WmlSphere3.h"
namespace Wml
{

using otf::Geom3d::Real;
using otf::Geom3d::Point;
using otf::Geom3d::Vector;

// Don't have to export Sphere3 because all methods are inlined
class Sphere3
{
public:
	Sphere3 ();

	Point& Center ();
	const Point& Center () const;

	Real& Radius ();
	const Real& Radius () const;

protected:
	Point m_kCenter;
	Real m_fRadius;
};

inline Sphere3::Sphere3 () { m_fRadius = 0; }
inline Point& Sphere3::Center () { return m_kCenter; }
inline const Point& Sphere3::Center () const { return m_kCenter; }
inline Real& Sphere3::Radius () { return m_fRadius; }
inline const Real& Sphere3::Radius () const { return m_fRadius; }

class WML_ITEM MinSphere3
{
public:
    MinSphere3 (int iQuantity, const Point* apkPoint,
        Sphere3& rkMinimal);
    // split original constructor into two
    MinSphere3 (int iQuantity, const Point** apkPerm,
        Sphere3& rkMinimal);
    template <class Iter> MinSphere3(Iter first, Iter last, Sphere3& rkMinimal);

    // Floating point tolerance used for various comparisons.  The default
    // value is 1e-03.
    static const Real EPSILON;

private:
    // indices of points that support current minimum volume sphere
    class WML_ITEM Support
    {
    public:
        bool Contains (int iIndex, const Point** apkPoint)
        {
            for (int i = 0; i < Quantity; ++i)
            {
                Vector kDiff = *apkPoint[iIndex] - *apkPoint[Index[i]];
                if ( kDiff.sqlength() < MinSphere3::EPSILON )
                    return true;
            }
            return false;
        }

        int Quantity;
        int Index[4];
    };

    // test if point P is inside sphere S
    static bool Contains (const Point& rkP,
        const Sphere3& rkS, Real& rfDistDiff);

    static Sphere3 ExactSphere1 (const Point& rkP);
    static Sphere3 ExactSphere2 (const Point& rkP0,
        const Point& rkP1);
    static Sphere3 ExactSphere3 (const Point& rkP0,
        const Point& rkP1, const Point& rkP2);
    static Sphere3 ExactSphere4 (const Point& rkP0,
        const Point& rkP1, const Point& rkP2,
        const Point& rkP3);

    static Sphere3 UpdateSupport1 (int i, const Point** apkPerm,
        Support& rkSupp);
    static Sphere3 UpdateSupport2 (int i, const Point** apkPerm,
        Support& rkSupp);
    static Sphere3 UpdateSupport3 (int i, const Point** apkPerm,
        Support& rkSupp);
    static Sphere3 UpdateSupport4 (int i, const Point** apkPerm,
        Support& rkSupp);

    typedef Sphere3 (*UpdateFunction)(int,const Point**,Support&);

    static UpdateFunction ms_aoUpdate[5];
    static const Real ONE_PLUS_EPSILON;
};

template <class Iter>
MinSphere3::MinSphere3(Iter first, Iter last, Sphere3& rkMinimal)
{
    if (first == last)
	assert (false);

    // create identity permutation (0,1,...,iQuantity-1)
    int iQuantity = std::distance(first, last);
    const Point** apkPerm = new const Point*[iQuantity];
    const Point** apkIndex = apkPerm;
    for (Iter i = first; i != last; ++i)
	*apkIndex++ = &*i;
    *this = MinSphere3(iQuantity, apkPerm, rkMinimal);
    delete [] apkPerm;
}

}

#endif /* WrapPy */

#endif
