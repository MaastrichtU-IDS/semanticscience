from chimera.tkoptions import BooleanOption, ColorOption, EnumOption, InfoOption, Option, IntOption
from _surface import SurfaceModel, SurfacePiece

# -----------------------------------------------------------------------------
#
class SurfaceSelectableOption(BooleanOption):
    name = 'selectable with mouse'
    attribute = 'piecesAreSelectable'
    balloon = 'whether surfaces are selectable with mouse'
    inClass = SurfaceModel

# -----------------------------------------------------------------------------
#
class SurfaceOneTransparentLayerOption(BooleanOption):
    name = 'one transparent layer'
    attribute = 'oneTransparentLayer'
    balloon = 'show only top layer of transparent surfaces'
    inClass = SurfaceModel

# -----------------------------------------------------------------------------
#
class SurfacePieceCountOption(InfoOption):
    name = 'pieces'
    attribute = 'pieceCount'
    balloon = 'number of pieces in surface'
    inClass = SurfaceModel
    def display(self, surfs):
        count = sum([len(s.surfacePieces) for s in surfs])
        self.set(' %d' % count)

# -----------------------------------------------------------------------------
#
class SurfaceTriangleCountOption(InfoOption):
    name = 'triangles'
    attribute = 'triangleCount'
    balloon = 'number of triangles in surface'
    inClass = SurfaceModel
    def display(self, surfs):
        count = sum([sum([p.triangleCount for p in s.surfacePieces])
                     for s in surfs])
        self.set(' %d' % count)

# -----------------------------------------------------------------------------
#
class PieceDisplayOption(BooleanOption):
    name = 'displayed'
    attribute = 'display'
    balloon = 'show/hide surface component'
    inClass = SurfacePiece

# -----------------------------------------------------------------------------
#
class PieceColorOption(ColorOption):
    name = 'color'
    attribute = 'color'
    balloon = 'surface piece color'
    inClass = SurfacePiece
    def getAttribute(self, piece, name):
        from chimera import MaterialColor
        return MaterialColor(*piece.color)
    def setAttribute(self, piece, name, value):
        piece.color = value.rgba()

# -----------------------------------------------------------------------------
#
class PieceStyleOption(EnumOption):
    name = 'display style'
    attribute = 'displayStyle'
    balloon = 'filled, mesh or dot surface style'
    inClass = SurfacePiece
    values = ('filled', 'mesh', 'dot')
    mapping = {SurfacePiece.Solid: 'filled',
               SurfacePiece.Mesh: 'mesh',
               SurfacePiece.Dot: 'dot',
               }
    def getAttribute(self, piece, name):
        return self.mapping[piece.displayStyle]
    def setAttribute(self, piece, name, value):
        style = [s for s,sname in self.mapping.items() if sname == value][0]
        piece.displayStyle = style

# -----------------------------------------------------------------------------
#
class PieceTransparencyModeOption(EnumOption):
    name = 'lighting, transparency'
    attribute = 'transparencyBlendMode'
    balloon = 'how much light do transparent layers reflect'
    inClass = SurfacePiece
    values = ('dim', 'bright')
    mapping = {SurfacePiece.SRC_1_DST_1_MINUS_ALPHA: 'bright',
               SurfacePiece.SRC_ALPHA_DST_1_MINUS_ALPHA: 'dim'}
    def getAttribute(self, piece, name):
        return self.mapping[piece.transparencyBlendMode]
    def setAttribute(self, piece, name, value):
        m = [mode for mode,mname in self.mapping.items() if mname == value][0]
        piece.transparencyBlendMode = m

# -----------------------------------------------------------------------------
#
class PieceSmoothLinesOption(BooleanOption):
    name = 'line smoothing'
    attribute = 'smoothLines'
    balloon = 'smooth jagged edges on lines if supported by hardware'
    inClass = SurfacePiece

# -----------------------------------------------------------------------------
#
class PieceLineThicknessOption(IntOption):
    name = 'line thickness'
    attribute = 'lineThickness'
    balloon = 'thickness of mesh lines in pixels'
    inClass = SurfacePiece
    min = 0

# -----------------------------------------------------------------------------
#
class PieceDotSizeOption(IntOption):
    name = 'dot size'
    attribute = 'dotSize'
    balloon = 'diameter of dots in pixels'
    inClass = SurfacePiece
    min = 0

# -----------------------------------------------------------------------------
#
class PieceLitOption(BooleanOption):
    name = 'lighting'
    attribute = 'useLighting'
    balloon = 'use directional light sources'
    inClass = SurfacePiece

# -----------------------------------------------------------------------------
#
class PieceTwoSidedLightingOption(BooleanOption):
    name = 'lighting, two sided'
    attribute = 'twoSidedLighting'
    balloon = 'light both sides of surface'
    inClass = SurfacePiece

# -----------------------------------------------------------------------------
#
class PieceTriangleCountOption(InfoOption):
    name = 'triangles'
    attribute = 'triangleCount'
    balloon = 'number of triangles in surface piece'
    inClass = SurfacePiece
    def display(self, pieces):
        count = sum([p.triangleCount for p in pieces])
        self.set(' %d' % count)

# -----------------------------------------------------------------------------
# Chimera selection inspector dialog requires class to be in chimera.triggers.
#
from chimera import triggers
for tname in (SurfaceModel.__name__, SurfacePiece.__name__):
    if not triggers.hasTrigger(tname):
        triggers.addTrigger(tname)

from chimera.tkoptions import inspectionInfo, registerOptions
inspectionInfo.register(SurfacePiece, displayAs = 'Surface piece')
inspectionInfo.register(SurfaceModel, displayAs = 'Surface')

registerOptions([
	SurfaceSelectableOption,
	SurfaceOneTransparentLayerOption,
	SurfacePieceCountOption,
	SurfaceTriangleCountOption,
	PieceDisplayOption,
	PieceColorOption,
	PieceStyleOption,
	PieceLineThicknessOption,
	PieceDotSizeOption,
	PieceSmoothLinesOption,
	PieceLitOption,
	PieceTwoSidedLightingOption,
	PieceTransparencyModeOption,
	PieceTriangleCountOption,
])
