#ifndef Chimera_LineType_h
# define Chimera_LineType_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

namespace chimera {

// LineType values match X3D specification.  And those match the
// "Linetype Section of the International Register of Graphical Items" 
// <http://jitc.fhu.disa.mil/nitf/graph_reg/graph_reg.htm#LINETYPE>.
enum LineType { SolidLine = 1, Dash, Dot, DashDot, DashDotDot, CustomLine = 16 };

// OpenGL stipple patterns for various line types
static const unsigned short Solid_Stipple = 0xffff;
static const unsigned short Dash_Stipple = 0x1f1f;
static const unsigned short Dot_Stipple = 0x0303;
static const unsigned short DashDot_Stipple = 0x0fc3;
static const unsigned short DashDotDot_Stipple = 0x3f33;

} // namespace chimera

#endif
