# Display proteins on a TkVisualizationCanvas

_undocumented = 1

from Scientific import N as Numeric

class ProteinBackboneGraphics:

    def __init__(self, protein, conf = None, color = None):
        self.protein = protein
        if conf is None:
            conf = protein.universe().configuration()
        self.points = conf.array

        if color is None:
            color = {}
            for a in protein.atomList():
                color[a.index] = a.color
        elif type(color) == type(''):
            color_name = color
            color = {}
            for a in protein.atomList():
                color[a.index] = color_name
        self.colors = color

        segments = []
        for chain in protein:
            segment = []
            segments.append(segment)
            last = None
            for residue in chain:
                atom = residue.peptide.C_alpha
                if last is None:
                    segment.append(atom.index)
                    last = atom
                else:
                    d = (last.position()-atom.position()).length()
                    if d < 0.4:
                        segment.append(atom.index)
                        last = atom
                    else:
                        last = None
                        segment = []
                        segments.append(segment)
        if len(segments[-1]) == 0:
            del segments[-1]
        self.segments = segments

    def project(self, axis, plane):
        self.depth = Numeric.dot(self.points, axis)
        self.projection = Numeric.dot(self.points, plane)

    def boundingBoxPlane(self):
        return Numeric.minimum.reduce(self.projection), \
               Numeric.maximum.reduce(self.projection)

    def scaleAndShift(self, scale=1, shift=0):
        self.scaled = scale*self.projection+shift

    def lines(self):
        lines = []
        depths = []
        for segment in self.segments:
            for i in range(len(segment)-1):
                i1 = segment[i]
                i2 = segment[i+1]
                p1 = self.scaled[i1]
                p2 = self.scaled[i2]
                c1 = self.colors[i1]
                c2 = self.colors[i2]
                depths.append(min(self.depth[i1], self.depth[i2]))
                if c1 == c2:
                    lines.append((p1[0], p1[1], p2[0], p2[1], c1, 1))
                else:
                    pc = 0.5*(p1+p2)
                    lines.append((p1[0], p1[1], pc[0], pc[1], c1, 1))
                    lines.append((pc[0], pc[1], p2[0], p2[1], c2, 1))
                    depths.append(depths[-1])
        return lines, depths


if __name__ == '__main__':

    pdbfile = '~/proteins/PDB/crambin.pdb'

    from mmtk import *
    from Tkinter import *
    from TkVisualizationCanvas import VisualizationCanvas

    universe = InfiniteUniverse()
    sequence = PDBFile(pdbfile).readSequenceWithConfiguration()
    chains = []
    for chain in sequence:
        model = PeptideChain(chain, model='calpha')
        chains.append(model)
    universe.protein = Protein(chains)

    clist = ['red', 'green', 'blue']
    colors = {}
    universe.configuration()
    for atom in universe.atomList():
        colors[atom.index] = clist[atom.index % len(clist)]

    graphics = ProteinBackboneGraphics(universe.protein, None, colors)

    window = Frame()
    window.pack(fill=BOTH, expand=YES)

    c = VisualizationCanvas(window, "100m", "100m", relief=SUNKEN, border=2)
    c.pack(side=TOP, fill=BOTH, expand=YES)
    c.draw(graphics)

    Button(window, text='Draw',
           command=lambda o=graphics: c.draw(o)).pack(side=LEFT)
    Button(window, text='Clear', command=c.clear).pack(side=LEFT)
    Button(window, text='Redraw', command=c.redraw).pack(side=LEFT)
    Button(window, text='Quit', command=window.quit).pack(side=RIGHT)

    window.mainloop()

