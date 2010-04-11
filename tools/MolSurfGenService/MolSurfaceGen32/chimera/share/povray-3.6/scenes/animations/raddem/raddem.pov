// Persistence Of Vision raytracer version 3.5 sample file.
// File by Dan Farmer
// Radiosity demonstration

// updated to 3.5 radiosity by Christoph Hormann

global_settings { assumed_gamma 2.2 }

#include "colors.inc"
#include "textures.inc"

#include "rad_def.inc"

global_settings {
  radiosity {
    Rad_Settings(Radiosity_Default, off, off)
    //Rad_Settings(Radiosity_Debug, off, off)
    //Rad_Settings(Radiosity_Fast, off, off)
    //Rad_Settings(Radiosity_Normal, off, off)
    //Rad_Settings(Radiosity_2Bounce, off, off)
    //Rad_Settings(Radiosity_Final, off, off)

    //Rad_Settings(Radiosity_OutdoorLQ, off, off)
    //Rad_Settings(Radiosity_OutdoorHQ, off, off)
    //Rad_Settings(Radiosity_OutdoorLight, off, off)
    //Rad_Settings(Radiosity_IndoorLQ, off, off)
    //Rad_Settings(Radiosity_IndoorHQ, off, off)
  }
}

camera {
  location <-1.5, 2, -29.9>
  direction z * 1.75
  up y
  right x * 1.3333
  look_at <0.5, -1.0, 0.0>
}

#declare Dist=15;
//#declare L = 0.65;
//#declare L = 0.35;
#declare L = 0.45;

light_source { <0, 9.5, 0>
  color rgb L
  fade_distance Dist fade_power 2
  shadowless
}

light_source { <-5, 7.5, 10.>
  color rgb L
  fade_distance Dist fade_power 2
  shadowless
}


//#declare Ambient = 0.35;
#declare Ambient = 0.0;

box { -1, 1
    scale <10, 10, 30>
    pigment { White }
    finish { ambient Ambient }
    inverse
}

box { -1, 1 scale <9, 8, 0.2>
    pigment {
        gradient z
        color_map {
            [0.0 color Red ]
            [0.5 color Red ]
            [0.5 color Blue ]
            [1.0 color Blue ]
        }
        translate -z*0.5
    }
    finish { ambient Ambient }
    rotate y*90
    rotate y*(clock*360)
    translate z*10
}

