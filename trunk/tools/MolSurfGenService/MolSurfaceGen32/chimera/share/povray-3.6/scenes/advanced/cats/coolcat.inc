// Persistence Of Vision Ray Tracer Scene Description File
// File: CoolCat.inc
// Vers: 3.5
// Desc: The parts of PovCat Ray
// Date: 1999/12/04
// Updated: 2001/07/27
// Auth: Ingo Janssen
//


#version 3.5;

//====== Some support macros ====
#macro Vmm(Min,Max,Value)
   (Min+((Max-Min)*Value))
#end

#macro InvRot(Rot)
   rotate <0,0,-Rot.z>
   rotate <0,-Rot.y,0>
   rotate <-Rot.x,0,0>
#end

//===
// r_ConnectSpheres (
//       radius_S1_sphere,
//       radius_S2_sphere,
//       Distance between spheres,
//       radius of Connection
// )
//
// The center of the S1_sphere is at the origin, the S2_sphere is somewhere on the y-axis
// In the scene, use r_ConnectSpheres inside a union or merge statement:
// union{r_ConnectSpheres(1, 0.5, 1.8, 0.4) pigment{color White}}

// This is what cats are made of.
#macro r_ConnectSpheres (r_S1, r_S2, Dist, r_Con, S1, S2)

  #local Selector= 0;
  #if ((Dist=0) & (r_S1 = r_S2))
    #debug "\n REMARK: The distance between spheres is zero and"
    #debug "\n         the radii of both spheres are equal. To"
    #debug "\n         avoid coincident surfaces, only one sphere"
    #debug "\n         will be traced."
    #debug "\n         Change the size of one of the spheres\n"
    #local Selector= 1;
  #end
  #if ((r_S1 >= r_S2 + abs(Dist)) & (Selector != 1))
    #debug "\n REMARK: The upper sphere is completeley enclosed,"
    #debug "\n         increase radius or dist."
    #debug "\n         Only one sphere will be visible.\n"
    #local Selector= 2;
  #end
  #if ((r_S2 >= r_S1 + abs(Dist)) & (Selector != 1))
    #debug "\n REMARK: The lower sphere is completeley enclosed,"
    #debug "\n         increase radius or dist."
    #debug "\n         Only one sphere will be visible.\n"
    #local Selector= 3;
  #end
  #if (r_Con <= abs(Dist)-r_S1-r_S2)
    #debug "\n REMARK: The connection radius is to"
    #debug "\n         small to connect both spheres."
    #debug "\n         Only two spheres will be visible, no connection.\n"
    #local Selector= 4;
  #end

  #switch (Selector)
    #case (0)
      #local r_Int_S1 = r_S1 + r_Con;
      #local r_Int_S2 = r_S2 + r_Con;

      #local Y1= (pow(Dist,3)-(Dist*r_Int_S2*r_Int_S2)+(Dist*r_Int_S1*r_Int_S1)) / (2*(Dist*Dist));
      #local X1= sqrt(abs((r_Int_S1*r_Int_S1)-(Y1*Y1)));

      #local XCone_S1= r_S1 / (r_S1+r_Con) * X1;
      #local YCone_S1= r_S1 / (r_S1+r_Con) * Y1;

      #local XCone_S2= r_S2 / (r_S2+r_Con) * X1;
      #local YCone_S2= (r_S2 / (r_S2+r_Con) * (Dist-Y1));
      #local YCone_S2= Dist-YCone_S2;

      difference {
        cone { <0,YCone_S1,0>, XCone_S1, <0,YCone_S2,0>, XCone_S2 }
        torus {
          X1, r_Con
          translate <0,Y1,0>
          sturm
        }
      }
      #if (S1 != false)
         sphere {<0,0,0>, r_S1}
      #end
      #if (S2 != false)
         sphere {<0,Dist,0>, r_S2}
      #end
    #break

    #case (1)
      #if (S1 != false)
         sphere {<0,0,0>, r_S1}
      #end
    #break

    #range (2,4)
      #if (S1 != false)
         sphere {<0,0,0>, r_S1}
      #end
      #if (S2 != false)
         sphere {<0,Dist,0>, r_S2}
      #end
    #break
  #end
#end


//=== Most positions are fixed, more or less,
//    the include is only written for PovCatRay.pov
//    and not as a complete animatible cat, with all
//    possible degrees of freedom in movement.

#ifndef (R_EarPos)    #declare R_EarPos    = < 0, 10, 45>;    #end
#ifndef (L_EarPos)    #declare L_EarPos    = < 0, 10,-45>;    #end
#ifndef (R_EarLength) #declare R_EarLength = 0.5;             #end  #if (R_EarLength= 0.2) R_EarLength= 0.2001 #end
#ifndef (L_EarLength) #declare L_EarLength = 0.5;             #end  #if (L_EarLength= 0.2) L_EarLength= 0.2001 #end

#ifndef (R_EyePos)    #declare R_EyePos    = <-70, 20, 0>;    #end
#ifndef (L_EyePos)    #declare L_EyePos    = <-70,-20, 0>;    #end

#ifndef (NosePos)     #declare NosePos     = <-100,  0, 0>;   #end

#ifndef (R_CheekPos)  #declare R_CheekPos  = <-115, 20, 0>;   #end
#ifndef (L_CheekPos)  #declare L_CheekPos  = <-115,-20, 0>;   #end

#ifndef (MouthPos)    #declare MouthPos    = < 0,-0.6,-0.35>; #end

//=== Animatable
#ifndef (PupilPos)    #declare PupilPos    =  <0, 0, 0>;      #end
#ifndef (PupilDiam)   #declare PupilDiam   =  0.048;          #end

#ifndef (R_EarTip)    #declare R_EarTip    = < 0, 0, 0>;      #end
#ifndef (L_EarTip)    #declare L_EarTip    = < 0, 0, 0>;      #end

#include "cattex.inc"

#declare R_InEar= union {
   r_ConnectSpheres( 0.25, 0.14, R_EarLength, 0.5, 1, 1)
   rotate R_EarTip
   translate < 0, 1,-0.2>
   texture {R_EarInTex}
}

#declare L_InEar= union {
   r_ConnectSpheres( 0.25, 0.14, L_EarLength, 0.5, 1, 1)
   rotate L_EarTip
   translate < 0, 1,-0.2>
   texture {L_EarInTex}
}

#declare Skull= difference {
   sphere {0,1}
   object {R_InEar rotate R_EarPos}
   object {L_InEar rotate L_EarPos}
   texture {CatTex}
}

#declare R_Ear= difference {
   union {
      union {
         r_ConnectSpheres( 1, 0.3, 1, 1.5, false, 1)
         texture {R_EarBaseTex}
      }
      union {
         r_ConnectSpheres( 0.3, 0.1, R_EarLength, 2, false, 1)
         rotate R_EarTip
         translate < 0, 1, 0>
         texture {R_EarTipTex}
      }
   }
   object {R_InEar}
   rotate R_EarPos
}

#declare L_Ear= difference {
   union {
      union {
         r_ConnectSpheres( 1, 0.3, 1, 1.5, false, 1)
         texture {L_EarBaseTex}
      }
      union {
         r_ConnectSpheres( 0.3, 0.1, L_EarLength, 2, false, 1)
         rotate L_EarTip
         translate < 0, 1, 0>
         texture {L_EarTipTex}
      }
   }
   object {L_InEar}
   rotate L_EarPos
}

#declare R_Eye= difference {
   union {
      r_ConnectSpheres( 1, 0.3, 0.8, 0.2, false, false)  // Eyelid
      sphere {   //Eyeball
         0,0.3
         texture {EyeTex}
         rotate PupilPos
         translate <0,0.8,0>
      }
   }
   sphere {0,1}
   texture {R_EyeLidTex}
   rotate R_EyePos
}

#declare L_Eye= difference {
   union {
      r_ConnectSpheres( 1, 0.3, 0.8, 0.2, false, false)  // Eyelid
      sphere {   //Eyeball
         0,0.3
         texture {EyeTex}
         rotate PupilPos
         translate <0,0.8,0>
      }
   }
   sphere {0,1}
   texture {L_EyeLidTex}
   rotate L_EyePos
}

#declare Nose= union {
   r_ConnectSpheres( 1, 0.2, 0.9, 1, false, 1)
   texture {NoseTex}
   rotate NosePos
}

#declare R_Cheek= union {
   r_ConnectSpheres( 1, 0.4, 0.8, 0.3, false, 1)
   texture {R_CheekTex}
   rotate R_CheekPos
}

#declare L_Cheek= union {
   r_ConnectSpheres( 1, 0.4, 0.8, 0.3, false, 1)
   texture {L_CheekTex}
   rotate L_CheekPos
}

#declare Mouth = torus {
   0.5,0.1
   scale <0.5,1,1>
   texture {MouthTex}
   translate MouthPos
}

#ifndef (Hair)
   #declare HairPart= union {
      sphere {
         0, 0.25
         scale < 1.3, 1, 0.3>
         translate <-0.15, 0, 0.01875>
      }
      sphere {
         0, 0.25
         scale < 1.3, 1, 0.3>
         translate < 0.15, 0,-0.01875>
      }
   }

   #declare Forelock= union {
      torus {
         0.2, 0.05
         rotate <90,0,0>
         scale < 1.3, 1, 1>
         translate <-0.15, 0, 0.01875>
      }
      torus {
         0.2, 0.05
         rotate <90,0,0>
         scale < 1.3, 1, 1>
         translate < 0.15, 0,-0.01875>
      }
   }

   #declare Hair= union {
      #declare i=0;
      #declare n=18;
      union {       //Forelock
         #while (i<n)
            object {
               Forelock
               scale <Vmm( 1, 0.5, i/n), Vmm( 1, 0.5, i/n), 1>
               translate < 0, 1, Vmm(0,-1,i/n)>
            rotate <-10, 0, 0>
            }
            #declare i=i+1;
         #end//while
      }
      #declare i=0;
      #declare n=40;
      union {       //upper hair
         #while (i<n)
            object {
               HairPart
               scale <Vmm( 1, 2, i/n), 1, 1>
               translate <0,1,0>
               rotate <Vmm(-10, 100, i/n), 0, 0>
            }
            #declare i=i+1;
         #end//while
      }
      #declare i=0;
      #declare n=20;
      union {       //lower hair
         #while (i<n)
            object {
               HairPart
               scale <Vmm( 2, 0.3, i/n), Vmm(1,0.5,i/n), 1>
               translate < 0, 1, 0>
               rotate <Vmm( 100, 140, i/n), 0, 0>
            }
            #declare i=i+1;
         #end//while
      }
      #declare i=0;
      #declare n=40;
      union {       //whiskers
         #while (i<n)
            object {
               HairPart
               scale <Vmm(0.5,0.1,i/n),Vmm(0.5,0.1,i/n),0.5>
               translate < 0, 1 ,0>
               rotate <Vmm(50,-40,i/n),0,Vmm(70,110,i/n)>
            }
            object {
               HairPart
               scale <Vmm(0.5,0.1,i/n),Vmm(0.5,0.1,i/n),0.5>
               translate < 0, 1 ,0>
               rotate <Vmm(50,-40,i/n),0,Vmm(-70,-110,i/n)>
            }
            #declare i=i+1;
         #end//while
      }
   }
#end//ifndef

#declare Cat= union {
   object {Skull}
   object {Hair texture {HairTex}}
   object {R_Ear}
   object {L_Ear}
   object {R_Eye}
   object {L_Eye}
   object {Nose}
   object {R_Cheek}
   object {L_Cheek}
   object {Mouth}
   scale < 0.9, 1, 0.8>
}
