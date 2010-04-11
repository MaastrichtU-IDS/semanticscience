// Persistence Of Vision Ray Tracer Scene Description File
// File: PovCatRay.pov
// Vers: 3.5
// Desc: A cool cat and his gang
// Date: 1999/12/04
// Updated: 2001/07/27
// Auth: Ingo Janssen
//
// -w320 -h240
// -w800 -h600 +a0.3
//

#version 3.5;
global_settings {assumed_gamma 1.0}
#include "cattext.inc"

// A basic hair creation macro
#macro Obj_RndOn_Sphere(r_Big, PlaceObj, TraceObj, n, S)
  #local R1=seed(S);
  #local Counter=0;
  #while (Counter != n)
    #local Angle= <rand(R1)*360,rand(R1)*360,rand(R1)*360>;
    #local OnSphere= vrotate(<0,r_Big,0>,Angle);
    #local TObj= trace(TraceObj,<0,0,0>, OnSphere);
    #if (TObj.x !=0 | TObj.y !=0 | TObj.z !=0)
      object {PlaceObj translate <0,r_Big,0> rotate Angle}
      #local Counter=Counter+1;
    #end
  #end
#end

light_source { < 500, 500,-500> rgb 1}
light_source { < 200, 500, 500> rgb 0.5}
light_source { < 0, 0,-500> rgb 0.2 shadowless}
light_source { <-500, 500,-500> rgb 0.1 shadowless}

camera {
   location  < 0, -0.2,-8.0>
   look_at   < 0, -0.2, 0.0>
   angle 35
}

#declare P= text {
   ttf
   "povlogo.ttf", "P",
   2, 0
   scale 0.8
   translate <0.25,0.05,-1>
}

#declare PP= pigment {
   object {
      P
      color rgb 0
      color rgb 0.1
    }
    warp {repeat x}
    warp {repeat y}
}

#declare Tor1Pos=transform {scale <0.9,1,1> translate <-0.9,0.1,0>}
#declare Tor2Pos=transform {scale < 0.8, 1, 1.5> scale 0.3 translate <1.7,1.1,0>}
#declare Tor3Pos=transform {scale 0.3 scale <0.9,1,1> translate <1.7,0.1,0>}
#declare Tor4Pos=transform {scale 0.3 scale <0.9,1,1> translate <1.7,-0.9,0>}

union {
   difference {
      plane {-z, 0 texture {pigment {checker pigment {rgb 0.7} pigment {PP} scale 0.25}}}
      sphere {0,1.5 scale 0.93 scale <1,1,2> transform Tor1Pos pigment {rgb <0,0,0.4>}}
      sphere {0,1.5 scale <1,1,2> transform Tor2Pos pigment {rgb <0.4,0,0>}}
      sphere {0,1.5 scale <1,1,2> transform Tor3Pos pigment {rgb <1,0.2,0>}}
      sphere {0,1.5 scale <1,1,2> transform Tor4Pos pigment {rgb <0,0.4,0>}}
   }
   torus {1.5,0.1 scale 0.93 rotate <90,0,0> transform Tor1Pos}
   torus {1.5,0.1 rotate <90,0,0> transform Tor2Pos}
   torus {1.5,0.1 rotate <90,0,0> transform Tor3Pos}
   torus {1.5,0.1 rotate <90,0,0> transform Tor4Pos}
   pigment {rgb 0.8}
   no_shadow
}

//==========================
//=== Cat1 = unmodified cat.
//==========================

#include "coolcat.inc"
object {
   Cat
   scale 0.93
   rotate <-5,-25, 0>
   translate <-0.9,-0.10,0>
}

//=========================
//===  Cat2
//=========================
#declare BaseTex= pigment {
   marble
   turbulence 0.4
   scale 0.2
   colour_map {
      [0, rgb 0.5]
      [1, rgb 0.8]
   }
}

#declare CatTex= texture {
   pigment {
      pigment_pattern {
         spherical
         scale <4,2,1.8>
         translate <0,-0.3,-0.7>
      }
      pigment_map {
         [0.7, BaseTex]
         [0.8, rgb 0.3]
      }
   }
}

#declare HairTex=texture {
   pigment {
      marble
      rotate <0,90,0>
      turbulence 0.4
      scale 0.2
      colour_map {
         [0, rgb 0.2]
         [1, rgb 0.05]
      }
   }
   finish {specular 0.2 roughness 0.08}
}

#declare Hair= difference {
   sphere {0,1.1}
   sphere {0,1.2 scale < 0.5, 3, 1.5> rotate < 0, 0, 40> translate <-0.3, 0,-1>}
   sphere {0,1.2 scale < 0.5, 3, 1.5> rotate < 0, 0,-40> translate < 0.3, 0,-1>}
   sphere {0,1.3 translate < 0,-1.37,-0.3>}
   sphere {0,0.32 translate < 0, 1, 0> rotate < 0, 0, 45>}
   sphere {0,0.32 translate < 0, 1, 0> rotate < 0, 0,-45>}
   scale <1,1,1.3>
}

#declare PupilPos    =  <-10,0,10>;
#declare PupilDiam   =  0.06;
#include "coolcat.inc"

object {
   Cat
   scale < 0.8, 1, 1.5>
   scale 0.3
   rotate <-10, 20, 0>
   translate <1.7,1,0>
}

#undef BaseTex
#undef CatTex
#undef HairTex
#undef Hair
#undef PupilPos
#undef PupilDiam

//==============================
//=== Cat3
//==============================
#declare CatTex= texture {
   pigment {
      spherical
      turbulence 0.3
      scale 1.5
      translate <0.2,0.2,-1>
      colour_map {
         [0.5, rgb 0.2]
         [0.8, rgb 0.8]
      }
   }
}
#declare HairTex= texture{pigment{rgb 0.8}}

#declare HairPiece= difference {
   sphere {0,1.1}
   sphere {0,1.2 scale < 0.5, 3, 1.5> rotate < 0, 0, 40> translate <-0.3, 0,-1>}
   sphere {0,1.2 scale < 0.5, 3, 1.5> rotate < 0, 0,-40> translate < 0.3, 0,-1>}
   sphere {0,1.3 translate < 0,-1.37,-0.3>}
   sphere {0,0.32 translate < 0, 1, 0> rotate < 0, 0, 45>}
   sphere {0,0.32 translate < 0, 1, 0> rotate < 0, 0,-45>}
   sphere {0,1}
   scale <1,1,1.3>
}
#declare OneHair= sphere {0,0.05 scale <1,2,1>}

#declare Hair= union {
   Obj_RndOn_Sphere(1,OneHair,HairPiece,1001,7)
}
#declare PupilPos    =  <0,0, 10>;
#declare PupilDiam   =  0.06;

#include "coolcat.inc"

object {
   Cat
   scale 0.3
   rotate <0, 20, 0>
   translate <1.7,0,0>
}

#undef CatTex
#undef HairTex
#undef HairPiece
#undef OneHair
#undef Hair
#undef PupilPos
#undef PupilDiam

//=================================
//=== Cat4
//=================================
#declare CatTex = texture {
   pigment {
      leopard
      turbulence 0.3
      scale 0.09
      colour_map {
         [0, rgb 0.4]
         [1, rgb 0.9]
      }
   }
}

#declare HairTex= texture {pigment {rgb 0.1}}

#declare HairPiece= intersection {
   difference {
      union {
         sphere {0,1 scale <0.2,1,1> translate < 0,1,0.1>}
         sphere {0,1 scale <0.1,1,1> translate <-0.3,1,0.2>}
         sphere {0,1 scale <0.1,1,1> translate < 0.3,1,0.2>}
         sphere {0,1 scale <2,0.5,0.2> translate <-0.5,-0.3,-0.20>}
      }
      sphere {0,1}
   }
   sphere {0,1.001}
}
#declare OneHair= mesh {triangle {<-0.005,0,0>,<0,0.2,0>,<0.005,0,0>}pigment{rgb 1}}

#declare Hair= union {
   Obj_RndOn_Sphere(1,OneHair,HairPiece,5000,7)
}

#declare PupilPos    =  <10,0, 10>;
#declare PupilDiam   =  0.08;
#declare L_EarTip    = <-20, 0,-30>;
#include "coolcat.inc"

object {
   Cat
   scale < 0.8, 1, 1.5>
   scale 0.3
   rotate < 10, 23, 0>
   translate <1.7,-1,0>
}

#undef CatTex
#undef HairTex
#undef HairPiece
#undef OneHair
#undef Hair
#undef PupilPos
#undef PupilDiam
#undef L_EarTip

//================================
//===Text
//================================
object {
   RayText
   no_shadow
   scale (1/346)*2.6
   rotate <0,0,15>
   translate <-0.7,-1.35,-0.3>
}
object {
   AndText
   no_shadow
   scale (1/51)*0.7
   scale <1,1,0.2>
   translate <0.5,-1.35,-0.28>
}
object {
   TBTrioText
   no_shadow
   scale (1/537)*2
   translate <1.1,-1.65,-0.3>
}
