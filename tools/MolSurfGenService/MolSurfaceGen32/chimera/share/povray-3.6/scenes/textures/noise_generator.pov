//	Persistence of Vision Raytracer Version 3.5 Scene Description File
//	File: noise_generator.pov
//	Last updated: 4/8/01
//	Author: Chris Huff
//	Description: A demo of the noise_generator feature.
//	The left column uses noise_generator 1, the old version of noise.
//	The middle column uses noise_generator 2, the MegaPOV corrected version.
//	The right column uses noise_generator 3, the new Perlin noise.
//
// -w320 -h240
// -w800 -h600 +a0.3
//
//*******************************************

#version 3.5;

#include "colors.inc"

//-------------------------------------------
global_settings {
	assumed_gamma 1
}

sphere {< 0, 0, 0>, 1 hollow
	texture {
		pigment {wrinkles
			color_map {
				[0 color rgb < 1, 1, 1>]
				[0.1 color rgb < 1, 1, 1>]
				[0.5 color rgb < 0.5, 0.75, 1>]
				[1 color rgb < 0.5, 0.75, 1>]
			}
		}
		finish {ambient 1 diffuse 0}
		scale < 1, 0.3, 1>*0.3
	}
	scale 1000
}

#declare CamLoc = < 0, 0,-6.5>;

camera {
	location CamLoc
	up y*image_height/image_width right x
	angle 65
	look_at < 0, 0, 0>
}

light_source {CamLoc color White*0.5}
light_source {<-50, 150,-75> color White}
//*******************************************

#declare Scale = 0.3;
union {
	sphere {< 0, 2, 0>, 1
		texture {
			pigment {wrinkles noise_generator 1
				scale Scale
				color_map {
					[0 color rgb 0]
					[1 color rgb 1]
				}
			}
			finish {ambient 0 diffuse 0.8}
		}
	}
	sphere {< 0, 0, 0>, 1
		texture {
			pigment {bozo noise_generator 1
				scale Scale
				color_map {
					[0 color rgb 0]
					[1 color rgb 1]
				}
			}
			finish {ambient 0 diffuse 0.8}
		}
	}
	sphere {< 0,-2, 0>, 1
		texture {
			pigment {agate noise_generator 1
				scale Scale
				color_map {
					[0 color rgb 0]
					[1 color rgb 1]
				}
			}
			finish {ambient 0 diffuse 0.8}
		}
	}
	translate -x*2.5
}
union {
	sphere {< 0, 2, 0>, 1
		texture {
			pigment {wrinkles noise_generator 2
				scale Scale
				color_map {
					[0 color rgb 0]
					[1 color rgb 1]
				}
			}
			finish {ambient 0 diffuse 0.8}
		}
	}
	sphere {< 0, 0, 0>, 1
		texture {
			pigment {bozo noise_generator 2
				scale Scale
				color_map {
					[0 color rgb 0]
					[1 color rgb 1]
				}
			}
			finish {ambient 0 diffuse 0.8}
		}
	}
	sphere {< 0,-2, 0>, 1
		texture {
			pigment {agate noise_generator 2
				scale Scale
				color_map {
					[0 color rgb 0]
					[1 color rgb 1]
				}
			}
			finish {ambient 0 diffuse 0.8}
		}
	}
}
union {
	sphere {< 0, 2, 0>, 1
		texture {
			pigment {wrinkles noise_generator 3
				scale Scale
				color_map {
					[0 color rgb 0]
					[1 color rgb 1]
				}
			}
			finish {ambient 0 diffuse 0.8}
		}
	}
	sphere {< 0, 0, 0>, 1
		texture {
			pigment {bozo noise_generator 3
				scale Scale
				color_map {
					[0 color rgb 0]
					[1 color rgb 1]
				}
			}
			finish {ambient 0 diffuse 0.8}
		}
	}
	sphere {< 0,-2, 0>, 1
		texture {
			pigment {agate noise_generator 3
				scale Scale
				color_map {
					[0 color rgb 0]
					[1 color rgb 1]
				}
			}
			finish {ambient 0 diffuse 0.8}
		}
	}
	translate x*2.5
}
