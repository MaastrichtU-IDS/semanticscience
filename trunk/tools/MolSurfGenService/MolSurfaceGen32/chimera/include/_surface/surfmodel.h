// ----------------------------------------------------------------------------
//
#ifndef SURFMODEL_HEADER_INCLUDED
#define SURFMODEL_HEADER_INCLUDED

#include <Python.h>			// use PyObject

#include <set>				// use std::set<>
#include <string>			// use std::string
#include <vector>			// use std::vector

#include <_chimera/Material.h>		// use Material
#include <_chimera/Model.h>		// use Model, BBox, Sphere
#include <_chimera/Notifier.h>		// use Notifier
#include <_chimera/Selectable.h>	// use Selectable
#include <_chimera/TrackChanges.h>	// use TrackChanges
#include <otf/WrapPy2.h>		// use WrapPyObj

#include "surfmodel_config.h"		// use SURFMODEL_IMEX
#include "surfrenderer.h"		// use Surface_Renderer

#ifdef WrapPy
//
// WrapPy does not follow include files.  I have to explicitly declare
// Model for WrapPy to use a wrapped version of that class.
//
namespace chimera
{
class Model : public Selectable
{
	// ABSTRACT
};
class Selectable: public otf::WrapPyObj
{
	// ABSTRACT
};
class ColorGroup: public otf::WrapPyObj
{
	// ABSTRACT
};
class Lens: public otf::WrapPyObj
{
	// ABSTRACT
};
class Material: public ColorGroup
{
};
class BBox
{
};
class Point
{
};
class Sphere
{
};

enum Selector;
}
#endif		// WrapPy

namespace Surface_Display
{

class SurfacePiece;

// ----------------------------------------------------------------------------
//
class SURFMODEL_IMEX SurfaceModel : public chimera::Model
{
  // BASE CLASS
 public:

  SurfaceModel();
  virtual ~SurfaceModel();

  const chimera::Material *material() const;	// Lighting parameters
  void setMaterial(const chimera::Material *m);

  bool piecesAreSelectable() const;
  void setPiecesAreSelectable(bool selectable);

  bool oneTransparentLayer() const;
  void setOneTransparentLayer(bool ol);

  SurfacePiece *newPiece();
  SurfacePiece *addPiece(PyObject *vertices, PyObject *vertex_indices,
			 PyObject *rgba);
  void removePiece(SurfacePiece *g);
  std::vector<SurfacePiece *> surfacePieces();	// ATTRIBUTE: surfacePieces

  void addGeometryChangedCallback(PyObject *cb);
  void removeGeometryChangedCallback(PyObject *cb);
  void callGeometryChangedCallbacks(SurfacePiece *p, const char *type);

  virtual bool computeBounds(/*OUT*/ chimera::Sphere *s,
			     /*OUT*/ chimera::BBox *box) const;
  virtual bool frontPoint(const chimera::Point &p1, const chimera::Point &p2,
			  /*OUT*/ float *frac) const;

#ifndef WrapPy
  void request_redraw(const chimera::NotifierReason &reason);

  const std::set<SurfacePiece *> &surface_piece_set() const;
  Surface_Renderer *renderer() const;

  virtual void wpyAssociate(PyObject* o) const;
  virtual PyObject* wpyNew() const;
  virtual chimera::Selectable::Selectables oslChildren() const;
  virtual chimera::Selectable::Selectables oslParents() const;
#endif

 private:
  virtual chimera::LensModel *newLensModel(chimera::Lens *l);

  bool selectable;		// whether surface pieces are selectable
  Surface_Renderer *sr;
  std::set<SurfacePiece *> pieces;
  std::vector<PyObject *> geometry_callbacks;

  chimera::Material mat;
  
  class Material_Changed : public chimera::Notifier
    {
    public:
      virtual void update(const void *surf_model, void *mat,
			  const chimera::NotifierReason &reason) const;
    } material_changed;

  typedef std::map<chimera::Lens *, chimera::LensModel *> LensModels;
  LensModels lensModels;

  static chimera::TrackChanges::Changes *const changes;
  static chimera::NotifierReason MATERIAL_CHANGED;
  static chimera::NotifierReason SELECTABLE_PIECES_CHANGED;
  static chimera::NotifierReason ONE_TRANSPARENT_LAYER_CHANGED;
  static chimera::NotifierReason PIECE_ADDED;
  static chimera::NotifierReason PIECE_REMOVED;
  virtual void trackReason(const chimera::NotifierReason &reason) const;

 public:
  static chimera::NotifierReason PIECE_CHANGED;
};

// ----------------------------------------------------------------------------
//
class SURFMODEL_IMEX SurfacePiece : public chimera::Selectable
{
 public:
#ifndef WrapPy
  SurfacePiece(SurfaceModel *sm, Surface_Renderer::Piece *g);
  virtual ~SurfacePiece();
  Surface_Renderer::Piece *piece() const;
#endif

  SurfaceModel *model() const;		// ATTRIBUTE: model

  bool display() const;
  void setDisplay(bool show);

  PyObject *geometry() const;	// Returns Numeric arrays of vertices (n by 3)
				//   and triangle vertex indices (m by 3).
  // TODO: Use wrappy non-attribute comment instead of returning None.
  void setGeometry(PyObject *vertices, PyObject *vertex_indices);
  int triangleCount() const;		// ATTRIBUTE: triangleCount

  PyObject *normals() const;	// N by 3 array of vertex normal vectors
  void setNormals(PyObject *normals);
    
  enum DisplayStyle { Solid, Mesh, Dot };
  DisplayStyle displayStyle() const;
  void setDisplayStyle(DisplayStyle style);

  //
  // For single color surface pieces.
  //
  void color(/*OUT*/ float *r, /*OUT*/ float *g,
	     /*OUT*/ float *b, /*OUT*/ float *a);
  void setColor(float r, float g, float b, float a);

  //
  // Vertex colors override the single color specification.
  // The vertex_rgba array has size N by 4 for a surface of N vertices.
  // To return to a single color surface set vertex colors to None.
  //
  PyObject *vertexColors();	// Numeric array of vertex rgba values.
  void setVertexColors(PyObject *vertex_rgba);

  //
  // Coloring with a texture overrides vertex and single color mode.
  // The texture coordinates array has size N by D for a surface of
  // N vertices and a texture of dimension D.
  // The texture id is an OpenGL texture id.
  // The transparency setting determines if texture alpha is used.
  // The modulation color is useful for non-white luminance textures.
  // The border color is for values outside the texture bounds.
  //
  PyObject *textureCoordinates();	// Array of float coords.
  void setTextureCoordinates(PyObject *texture_coords);
  unsigned int textureId() const;
  void setTextureId(unsigned int tid);
  bool useTextureTransparency() const;
  void setUseTextureTransparency(bool transp);
  PyObject *textureModulationColor() const;
  void setTextureModulationColor(PyObject *rgba);
  PyObject *textureBorderColor() const;
  void setTextureBorderColor(PyObject *rgba);

  bool useLighting() const;
  void setUseLighting(bool use);

  bool twoSidedLighting() const;
  void setTwoSidedLighting(bool two_sided);

  float lineThickness() const;
  void setLineThickness(float thickness);

  float dotSize() const;
  void setDotSize(float size);

  bool smoothLines() const;
  void setSmoothLines(bool smooth);

  enum BlendMode { SRC_1_DST_1_MINUS_ALPHA, SRC_ALPHA_DST_1_MINUS_ALPHA };
  BlendMode transparencyBlendMode() const;
  void setTransparencyBlendMode(BlendMode bmode);

  // maskedGeometry() returns arrays of vertices (n by 3) and triangle vertex
  // indices (m by 3) or edge vertex indices (m by 2) or dot vertex indices
  // (m by 1).
  PyObject *maskedGeometry(DisplayStyle style) const;

  // Can turn off display of individual triangles or mesh edges.
  // Triangle and edge mask is a one dimensional array with length equal
  // to number of triangles used.
  // Bits 0, 1, 2 control edges 0-1, 1-2, 2-0.
  // Bit 3 controls triangle display.
  // A hidden triangle hides the triangle's edges.
  PyObject *triangleAndEdgeMask();
  void setTriangleAndEdgeMask(PyObject *mask);
  void setEdgeMask(PyObject *mask);

  //
  // The vertex mask array has length equal to the number of surface vertices
  // and values 1 and 0 indicating whether the vertex is displayed or not.
  // To show all vertices pass None as the array argument.
  //
  void setTriangleMaskFromVertexMask(PyObject *mask);

  bool bbox(/*OUT*/ chimera::BBox *b) const;
  bool bsphere(/*OUT*/ chimera::Sphere *s) const;
  bool frontPoint(const chimera::Point &p1, const chimera::Point &p2,
		  /*OUT*/ float *frac) const;

#ifndef WrapPy
  void geometryChanged();	// Invokes callbacks
  virtual PyObject* wpyNew() const;
  virtual std::string oslIdent(chimera::Selector start, chimera::Selector end) const;
  virtual chimera::Selectable::Selectables oslChildren() const;
  virtual chimera::Selectable::Selectables oslParents() const;
  virtual bool oslTestAbbr(chimera::OSLAbbreviation *a) const;
  virtual chimera::Selector oslLevel() const;
#endif
  static const chimera::Selector selLevel = chimera::SelVertex;
  std::string oslName() const;
  void setOslName(std::string name);

 private:
  SurfaceModel *sm;
  Surface_Renderer::Piece *g;
  std::string osl_name;

  static chimera::TrackChanges::Changes *const changes;
  static chimera::NotifierReason GEOMETRY_CHANGED;
  static chimera::NotifierReason DISPLAY_STYLE_CHANGED;
  static chimera::NotifierReason DISPLAY_CHANGED;
  static chimera::NotifierReason COLOR_CHANGED;
  static chimera::NotifierReason DISPLAY_MASK_CHANGED;
  static chimera::NotifierReason VERTEX_COLORS_CHANGED;
  static chimera::NotifierReason TEXTURE_COORDINATES_CHANGED;
  static chimera::NotifierReason TEXTURE_ID_CHANGED;
  static chimera::NotifierReason TEXTURE_TRANSPARENCY_CHANGED;
  static chimera::NotifierReason TEXTURE_MODULATION_COLOR_CHANGED;
  static chimera::NotifierReason TEXTURE_BORDER_COLOR_CHANGED;
  static chimera::NotifierReason USE_LIGHTING_CHANGED;
  static chimera::NotifierReason TWO_SIDED_LIGHTING_CHANGED;
  static chimera::NotifierReason SMOOTH_LINES_CHANGED;
  static chimera::NotifierReason LINE_THICKNESS_CHANGED;
  static chimera::NotifierReason DOT_SIZE_CHANGED;
  static chimera::NotifierReason TRANSPARENCY_MODE_CHANGED;
  static chimera::NotifierReason NORMALS_CHANGED;
  virtual void trackReason(const chimera::NotifierReason &reason) const;

  void request_redraw(const chimera::NotifierReason &reason) const;

#ifdef WrapPy
  SurfacePiece();		// Prevent WrapPy from making a contructor
  virtual ~SurfacePiece();	// Prevent WrapPy from making a destructor
#endif
};

}	// end of namespace Surface_Display

#endif
