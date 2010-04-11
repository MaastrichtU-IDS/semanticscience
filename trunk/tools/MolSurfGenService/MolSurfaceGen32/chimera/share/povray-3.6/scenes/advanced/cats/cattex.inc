// Persistence Of Vision Ray Tracer Scene Description File
// File: CatTex.inc
// Vers: 3.5
// Desc: Texures for PovCat Ray
// Date: 1999/12/04
// Updated: 2001/07/27
// Auth: ingo
//

#version 3.5;

#ifndef (CatTex)
   #declare CatTex= texture {
      pigment {
         wood rotate <91,0,0> translate <0,20,0>
         turbulence 0.05
         scale 0.3
         colour_map {
            [0.1, rgb 0.75]
            [1, rgb 0.3]
         }
      }
   }
#end

#ifndef (HairTex)
   #declare HairTex= texture {
      pigment {
         wood rotate <91,0,0> translate <0,20,0>
         turbulence 0.05
         scale 0.3
         colour_map {
            [0.1, rgb 0.05]
            [1, rgb 0.02]
         }
      }
      finish {phong 1 phong_size 60}
   }
#end

#declare R_EarBaseTex= texture {
   CatTex
   InvRot(R_EarPos)
}
#declare R_EarTipTex= texture {
   CatTex
   translate <0,-1,0>
   InvRot(R_EarTip)
   InvRot(R_EarPos)
}
#declare R_EarInTex= texture {
   CatTex
   translate <0,-1,0.2>
   InvRot(R_EarTip)
   InvRot(R_EarPos)
}

#declare L_EarBaseTex= texture {
   CatTex
   InvRot(L_EarPos)
}
#declare L_EarTipTex= texture {
   CatTex
   translate <0,-1,0>
   InvRot(L_EarTip)
   InvRot(L_EarPos)
}
#declare L_EarInTex= texture {
   CatTex
   translate <0,-1,0.2>
   InvRot(L_EarTip)
   InvRot(L_EarPos)
}

#declare EyeTex= texture {
   pigment {
      cylindrical
      colour_map {
         [1-PupilDiam, rgb <1,1,0.95>]
         [1-PupilDiam, rgb 0]
      }
   }
   finish {phong 1 phong_size 60}
}

#declare R_EyeLidTex= texture {
   cylindrical
   texture_map {
      [0.73, CatTex InvRot(R_EyePos)]
      [0.78, pigment {rgb 0} finish {phong 1 phong_size 30}]
   }
}

#declare L_EyeLidTex= texture {
   cylindrical
   texture_map {
      [0.73, CatTex InvRot(L_EyePos)]
      [0.78, pigment {rgb 0}]
   }
}

#declare NoseTex= texture {
   pigment_pattern {
      cylindrical
      scale <1.5,1,1>
      rotate <-4,0,0>
   }
   texture_map {
      [0.8, CatTex InvRot(NosePos)]
      [0.98, pigment {rgb 1}]
      [0.90, pigment {rgb 0.05} finish {phong 1}]
   }
}

#declare R_CheekTex= texture {
   pigment_pattern {
      cylindrical
      scale <1.5,1,1>
      rotate <-10,20,0>
   }
   texture_map {
      [0.65, CatTex InvRot(R_CheekPos)]
      [1, CatTex InvRot(R_CheekPos) normal {bumps 0.25 scale 0.02}]
   }
}

#declare L_CheekTex= texture {
   cylindrical
   texture_map {
      [0.65, CatTex InvRot(L_CheekPos)]
      [1, CatTex InvRot(L_CheekPos) normal {bumps 0.25 scale 0.02}]
   }
}

#declare MouthTex= texture {
   CatTex
   translate -1*MouthPos
   normal {
      bumps 0.2
      scale 0.02
   }
}
