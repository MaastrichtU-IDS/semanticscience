#ifndef Chimera_PrimitiveCache_h
# define Chimera_PrimitiveCache_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# ifndef WrapPy

# include "_chimera_config.h"

namespace chimera {

enum Primitives {
	Ball, Cylinder, Disk, LineWidth, PointSize, Cone, NumPrimitives
};

template <int p>
class CHIMERA_IMEX PrimitiveCache
{
public:
	static void	ref(float radius);
	static void	unref(float radius);
	static void	draw(float radius);
	static void	rebuild();
};

typedef PrimitiveCache<Ball> BallCache;
typedef PrimitiveCache<Cylinder> CylinderCache;
typedef PrimitiveCache<Disk> DiskCache;
typedef PrimitiveCache<LineWidth> LineWidthCache;
typedef PrimitiveCache<PointSize> PointSizeCache;
typedef PrimitiveCache<Cone> ConeCache;

template <> void BallCache::ref(float radius);
template <> void CylinderCache::ref(float radius);
template <> void DiskCache::ref(float radius);
template <> void LineWidthCache::ref(float size);
template <> void PointSizeCache::ref(float size);
template <> void ConeCache::ref(float radius);

extern int sphereSlices(float radius);
extern int sphereStacks(float radius, int slices);
extern int cylinderSlices(float radius);

#ifdef GLU_VERSION_1_1
extern GLUquadricObj *default_quadric();
#endif

} // namespace chimera

# endif /* WrapPy */

#endif
