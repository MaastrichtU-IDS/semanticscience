// Persistence Of Vision raytracer version 3.5 sample file.
//	File: fractals2.pov
//	Last updated: 6/5/02
//	Author: Juha Nieminen
//	Description:
// Demonstrates the use of fractal patterns.
// The fractals used are:
// - Wall: A magnet2m pigment with interior type 1.
// - Floor: A mandelbrot pigment and normal with
//   interior type 1.
//
// -w320 -h240
// -w800 -h600 +a0.3

global_settings {
  max_trace_level 5
}

camera { location <-2,5,-10>*1.4 look_at -y angle 35 }
light_source { <0,0,-.1>,<1,.95,.8> }

// Magnet2m:
plane
{ -z,0
  pigment
  { magnet 2 mandel 300
    color_map
    { [0 rgb -.5]
      [.2 rgb x]
      [.3 rgb x+y]
      [.5 rgb <.2,.5,.9>]
      [1 rgb 1]
    }
    interior 1,200000
    translate <-1.693285,-.69524>
    scale 10000
  }
  finish { ambient 1 }
}

// Mandel:
plane
{ y,-1
  texture
  { pigment
    { mandel 50
      interior 1,5
      color_map
      { [0 rgb <.4,.2,.1>]
        [.3 rgb <.8,.4,.1>]
        [.6 rgb <1,.8,.4>]
        [1 rgb 1]
      }
    }
    normal
    { mandel 80 1
      interior 1,5
      slope_map { [0 <0,0>][.5 <.5,1>][1 <1,0>] }
    }
    finish { specular 1 reflection .3 }

    translate <.2,-1>
    scale 10
    rotate x*90
  }
}

union
{ sphere { <3.5,-.5,-1>,.5 }
  sphere { <-3.5,-.5,-1>,.5 }
  pigment { rgb <.5,1,.5> }
  finish { specular .8 reflection .5 }
}
