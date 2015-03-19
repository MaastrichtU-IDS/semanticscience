Sets, classes, collections and aggregates aim to associate arbitrary entities together with different minimal criteria.

### types ###

**['set'](http://semanticscience.org/resource/SIO_000289)**

A set is an arbitrary collection of items (of any type), for which there may be zero members (aka empty set).

**['class'](http://semanticscience.org/resource/SIO_000138)**

A class is a set that is extensionally defined through one or more properties that all its members share.

**['collection'](http://semanticscience.org/resource/SIO_000616)**

A collection is a set for which i) there exists at least one member at any given time and ii) each item is of the same type.

**['aggregate'](http://semanticscience.org/resource/)**

An aggregate is a collection for which there exists at least two members at the same time.

### relations ###

**['has member'](http://semanticscience.org/resource/SIO_000059)**

items in a set/collection/aggregate are specified with the 'has member' relation.


### examples ###

If a collection contains only one kind of member, then we can write a class axiom like
```
'Collection of x-type valued items'
 equivalentClass
 'collection'
 and 'has member' some ('x' and 'has value' some Literal)
 and 'has member' only ('x' and 'has value' only Literal)
```

If a collection consists of values that must be paired together, we can write:
```
'Collection of xy-valued-pairs'
 equivalentClass 
   'collection' 
   and 'has member' some ('xy-pair' 
      and 'has component part' some ('x' and 'has value' some Literal)
      and 'has component part' some ('y' and 'has value' some Literal)
   )
```

example instantiation (in pretty turtle syntax]:
```
:cxy a 'Collection of xy-valued-pairs' ;
  'has member' [ a 'xy-pair'; 
      'has component part' [ a 'x'; 'has value' 1^^xsd:int] ;
      'has component part' [ a 'y'; 'has value' 2^^xsd:int] ;
   ] .
```