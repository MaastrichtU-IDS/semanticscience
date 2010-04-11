//	Persistence of Vision Raytracer Version 3.5 Scene Description File
//	File: media3.pov
//	Author:
//	Description:
// This scene shows the effect of a partially transparent image
// map inside a participating medium.
//
// -w320 -h240
// -w800 -h600 +a0.3
//
//*******************************************

//
// The camera.
//

camera {
  location <0, 3, -10>
  look_at <0, -0.5, 0>
  angle 10
}

//
// Add media.
//

box {<-2,-0.999,-2>, < 2, 0.001, 2>
	texture {pigment {color rgbf 1}}
	hollow
	interior {
		media {
			scattering { 1, rgb 0.2}
			intervals 1
			samples 20
			method 3
		}
	}
}


//
// A shadowless light source that does not interact with the atmosphere.
//

light_source { <100, 100, -100> color rgb 0.3
  media_interaction off
  shadowless
}

//
// A spotlight pointing at the image map.
//

light_source {
  <0, 5, 0>
  color rgb 4
  spotlight
  point_at <0, 0, 0>
  falloff 10
  radius 8
  media_interaction on
}

//
// The partially translucent image map.
//

polygon {
  5, <-1, -1, 0>, <1, -1, 0>, <1, 1, 0>, <-1, 1, 0>, <-1, -1, 0>
  pigment {
    image_map {
      png "test.png"
      once
      transmit 5, 1
    }
    translate <-0.5, -0.5, 0>
  }
  scale 2
  rotate 90*x
  hollow
}

//
// The ground.
//

plane { y, -1 pigment { color rgb 1 } hollow }



