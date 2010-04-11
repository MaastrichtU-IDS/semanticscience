// Persistence Of Vision raytracer version 3.5 sample file.
// File: micro.pov
// Author: Chris Huff
// Desc: Playing with emitting media...resembles something under a microscope
//
// -w320 -h240
// -w800 -h600 +a0.3

#include "colors.inc"
#include "functions.inc"

#version 3.5;

global_settings {
    assumed_gamma 1
}

#default {finish {ambient 0}}

#declare CamPos = < 0, 0,-4.5>;

camera {
    location CamPos
    look_at < 0, 0, 0>
    angle 35
}

#declare Th1 = 0.0;
#declare Th2 = 0.05;

box {<-1,-1,-1>, < 1, 1, 1>
    texture {pigment {color rgbf 1}}
    hollow
    interior {
        media {
            emission color rgb < 0.5, 1, 0.1>*1.75
            intervals 2 samples 32
            method 3
            aa_threshold 0.1 aa_level 5
            density {crackle
                scale 0.5 translate y*24
                color_map {
                    [0 rgb 0]
                    [Th1 rgb 0]
                    [Th1 rgb 1]
                    [Th2 rgb 1]
                    [Th2 rgb 0]
                    [1 rgb 0]
                }
            }
            density {spherical
                color_map {
                    [0 rgb 0]
                    [0.4 rgb 1]
                    [1 rgb 1]
                }
            }
        }
        media {
            emission color rgb < 1, 0.5, 0.1>*1.75
            intervals 2 samples 32
            method 3
            aa_threshold 0.1 aa_level 5
            density {crackle
                scale 0.5
                color_map {
                    [0 rgb 0]
                    [Th1 rgb 0]
                    [Th1 rgb 1]
                    [Th2 rgb 1]
                    [Th2 rgb 0]
                    [1 rgb 0]
                }
            }
            density {spherical
                color_map {
                    [0 rgb 0]
                    [0.4 rgb 1]
                    [1 rgb 1]
                }
            }
        }
        media {
            emission color rgb < 0.5, 0.75, 1>*0.5
            intervals 2 samples 32
            method 3
            aa_threshold 0.1 aa_level 5
            density {spherical
                color_map {
                    [0 rgb 0]
                    [0.01 rgb 1]
                    [0.05 rgb 1]
                    [0.05 rgb 0]
                    [1 rgb 0]
                }
            }
        }
    }
}

