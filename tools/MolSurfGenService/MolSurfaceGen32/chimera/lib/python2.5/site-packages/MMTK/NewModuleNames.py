# Translate old to new module names for unpickling.
#
# Written by Konrad Hinsen
# last revision: 2005-11-7
#

_undocumented = 1

new_name = {
    ("Vector", "Vector"): ("Scientific.Geometry", "Vector"),
    ("Tensor", "Tensor"): ("Scientific.Geometry", "Tensor"),
    ("Transformation", "Translation"):
                ("Scientific.Geometry.Transformation", "Translation"),
    ("Transformation", "Rotation"):
                ("Scientific.Geometry.Transformation", "Rotation"),
    ("Transformation", "RotationTranslation"):
                ("Scientific.Geometry.Transformation", "RotationTranslation"),
    ("TensorAnalysis", "ScalarField"):
                ("Scientific.Geometry.TensorAnalysis", "ScalarField"),
    ("TensorAnalysis", "VectorField"):
                ("Scientific.Geometry.TensorAnalysis", "VectorField"),
    ("Color", "Color"): ("Scientific.Visualization.Color", "Color"),
    ("Variables", "ParticleScalar"):
                ("MMTK.ParticleProperties", "ParticleScalar"),
    ("Variables", "ParticleVector"):
                ("MMTK.ParticleProperties", "ParticleVector"),
    ("MMTK.Variables", "ParticleScalar"):
                ("MMTK.ParticleProperties", "ParticleScalar"),
    ("MMTK.Variables", "ParticleVector"):
                ("MMTK.ParticleProperties", "ParticleVector"),
    ("Protein", "Residue"): ("MMTK.Proteins", "Residue"),
    ("Protein", "PeptideChain"): ("MMTK.Proteins", "PeptideChain"),
    ("Protein", "ConnectedChains"): ("MMTK.Proteins", "ConnectedChains"),
    ("Protein", "Protein"): ("MMTK.Proteins", "Protein"),
    ("NucleicAcid", "Nucleotide"): ("MMTK.NucleicAcids", "Nucleotide"),
    ("NucleicAcid", "NucleotideChain"):
                          ("MMTK.NucleicAcids", "NucleotideChain"),
    ("AmberForceField", "AmberForceField"):
                          ("MMTK.ForceFields", "Amber94ForceField"),
    ("AmberForceField", "Amber94ForceField"):
                          ("MMTK.ForceFields", "Amber94ForceField"),
    ("AmberForceField", "Amber91ForceField"):
                          ("MMTK.ForceFields", "Amber91ForceField"),
    ("Deformation", "DeformationForceField"):
                          ("MMTK.ForceFields", "DeformationForceField"),
    ("SparseModes", "SparseMatrixNormalModes"):
                          ("MMTK.SparseModes", "SparseMatrixNormalModes"),
    ("mmtk", "InfiniteUniverse"): ("MMTK.Universe", "InfiniteUniverse"),
    ("mmtk", "CubicPeriodicUniverse"):
                          ("MMTK.Universe", "CubicPeriodicUniverse"),
    ("mmtk", "OrthorhombicPeriodicUniverse"):
                          ("MMTK.Universe", "OrthorhombicPeriodicUniverse"),
    ("mmtk", "AmberForceField"):
                          ("MMTK.ForceFields", "Amber94ForceField"),
    ("mmtk", "Atom"): ("MMTK.ChemicalObjects", "Atom"),
    ("mmtk", "Group"): ("MMTK.ChemicalObjects", "Group"),
    ("mmtk", "Molecule"): ("MMTK.ChemicalObjects", "Molecule"),
    ("mmtk", "Collection"): ("MMTK.Collections", "Collection"),
    ("mmtk", "Protein"): ("MMTK.Proteins", "Collection"),
    ("MMTK.Collection", "Collection"): ("MMTK.Collections", "Collection"),
    ("MMTK.Collection", "PartitionedCollection"):
                          ("MMTK.Collections", "PartitionedCollection"),
    ("MMTK.Collection", "PartitionedAtomCollection"):
                          ("MMTK.Collections", "PartitionedAtomCollection"),
    }
