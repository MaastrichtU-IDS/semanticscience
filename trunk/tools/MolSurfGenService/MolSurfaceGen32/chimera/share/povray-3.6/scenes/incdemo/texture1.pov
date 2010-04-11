// Persistence Of Vision raytracer version 3.5 sample file.
// The TEXTUREn.POV files demonstrate all textures in TEXTURES.INC
//
// -w320 -h240
// -w800 -h600 +a0.3

global_settings { 
  assumed_gamma 2.2 
  max_trace_level 5
}

#include "textures.inc"

#declare Textures=array[3][9]
{
  {
     texture { pigment { Jade                } },
     texture { pigment { Red_Marble          } },
     texture { pigment { White_Marble        } },

     texture { pigment { Blood_Marble        } },
     texture { pigment { Blue_Agate          } },
     texture { pigment { Sapphire_Agate      } },

     texture { pigment { Brown_Agate         } },
     texture { pigment { Pink_Granite        } },
     texture {           PinkAlabaster         }
  },
  {
     texture { pigment { Blue_Sky            } },
     texture { pigment { Bright_Blue_Sky     } },
     texture { pigment { Blue_Sky2           } },

     texture { pigment { Blue_Sky3           } },
     texture { pigment { Blood_Sky           } },
     texture { pigment { Apocalypse          } },

     texture { pigment { Clouds              } },
     texture { pigment { FBM_Clouds          } },
     texture {           Shadow_Clouds         }
  },
  {
     texture { pigment { Cherry_Wood         } },
     texture { pigment { Pine_Wood           } },
     texture { pigment { Dark_Wood           } },

     texture { pigment { Tan_Wood            } },
     texture { pigment { White_Wood          } },
     texture { pigment { Tom_Wood            } },

     texture { pigment { DMFWood1            } },
     texture { pigment { DMFWood2            } },
     texture { pigment { DMFWood3            } }
  }
}

#include "shotxtr.inc"
