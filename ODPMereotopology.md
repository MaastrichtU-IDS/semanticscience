Structural descriptions of objects in terms of their parts and how they are connected together is a basic requirement. SIO provides the following relations to precisely do this.

## mereology ##

**['has part'](http://semanticscience.org/resource/SIO_000028) / ['is part of'](http://semanticscience.org/resource/SIO_000068) [T|R]**

'has part' is a reflexive, transitive relation links an object to itself (reflexive) and all of its  parts (transitive). This means that query for the parts of the whole will include itself as well as all of its parts.


**['has proper part'](http://semanticscience.org/resource/SIO_000053) / ['is proper part of'](http://semanticscience.org/resource/SIO_000093) [T|IR|AS]**

'has proper part' is an irreflexive, asymmetric relation that ensures that the whole is different from and not one of its proper parts.


**['has direct part'](http://semanticscience.org/resource/SIO_000273) / ['is direct part of'](http://semanticscience.org/resource/SIO_000310)**

'has direct part' provides an avenue to quantify the number of parts (via a cardinality restriction) at a target type granularity.


**['has component part'](http://semanticscience.org/resource/SIO_000369) / ['is component part of'](http://semanticscience.org/resource/SIO_000313)**

'has component part' can be used to indicate that the part is intrinsic to the whole, and that the removal of the part changes the identity of the whole.

_examples_: Molecular identity necessarily depends on its atomic composition, so removing an atom from a molecule changes the kind of molecule that it is. In contrast, should a human lose a limb to an accident, this wouldn't change the fact that they are still human.


**['is located in'](http://semanticscience.org/resource/SIO_000061) / ['is location of'](http://semanticscience.org/resource/SIO_000145) [T](T.md)**

'is located in' is a transitive relation in which the 2D/3D spatial region occupied by one entity is a part of the 2D/3D spatial region occupied by another entity.


**['contains'](http://semanticscience.org/resource/SIO_000202) / ['is contained in'](http://semanticscience.org/resource/SIO_000128) [T](T.md)**

'contains' is a transitive relation in which the 3D spatial region occupied by A has the 3D spatial region occupied by B as a part, but it is not the case that A has B as a part.


**['surrounds'](http://semanticscience.org/resource/SIO_000324) / ['is surrounded by'](http://semanticscience.org/resource/SIO_000323)**

A 'surrounds' B iff the A 'contains' B and A 'is adjacent to' B or A 'is directly connected to' B.


## topology ##

While the 'has part' relation hierarchy is focused on identifying the parts of a whole, the next set of relations allows one to specify how the parts are positioned to one another.

**['is connected to'](http://semanticscience.org/resource/SIO_000203) [T|S]**

'is connected to' is a symmetric, transitive relation that specifies that components either directly share a boundary (they are directly connected to each other) or that they are indirectly connected by a path of unbroken direct connections.


**['is directly connected to'](http://semanticscience.org/resource/SIO_000652) `[S]`**

'is directly connected to' is a symmetric relation that indicates that two components share a boundary. Since this relation is nontransitive, we can use it in statements to quantify the number of connections from one part to other kinds of parts.

**['is directly before'](http://semanticscience.org/resource/SIO_000242) / ['is directly after'](http://semanticscience.org/resource/SIO_000241)**

'is directly before' is a relation between entities placed on a dimensional axis in which the projection of the position of the first entity is numerically less than the projection of the position of the second entity, and the entities are adjacent to one another. This is useful for indicating the spatial positioning of residues in linear biopolymers such as proteins or nucleic acids.


_molecule example_
```
'methane' 
 equivalentClass
 'molecule'
 and 'has component part' exactly 4 'methane hydrogen atom'
 and 'has component part' exactly 1 'methane carbon atom'
 and 'has component part' only ('part of' some 'methane carbon atom' or 'part of' some 'methane hydrogen atom')

'methane hydrogen atom'
 equivalentClass
 'hydrogen atom'
 and 'is component part of' exactly 1 'methane'
 and 'is covalently connected to' exactly 1 'methane carbon atom'

'methane carbon atom'
 equivalentClass
 'carbon atom'
 and 'is component part of' exactly 1 'methane'
 and 'is covalently connected to' exactly 4 'methane hydrogen atom'
```

_protein example_
```
'human p53 isoform 1'
 equivalentClass
 'protein'
 and 'has component part' exactly 1 ('human p53 isoform 1 methionine residue @ pos1')
 and 'has component part' exactly 1 ('human p53 isoform 1 glutamate residue @ p2')
 ...
 
'human p53 isoform 1 methionine residue @ p1'
 equivalentClass
 'methionine residue'  // use chebi 
 'is component part of' exactly 1 'human p53 isoform 1'
 and 'has attribute' exactly 1 ('position' and 'has value' value "1"^^xsd:int)
 and 'is directly before' exactly 1 ('human p53 isoform 1 glutamate residue @ p2')

...
```

_proteosome containment example_
```
 'proteosome-complex with peptide chain'
 subClassOf
 'protein complex'
 and 'has proper part' some ('proteosome' that 'contains' some 'peptide chain')
 and 'has proper part' some ('peptide chain' that 'is contained by' some 'proteosome')
```