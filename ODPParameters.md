Parameters are used to specify the behavior of some application. This is of particular relevance in modeling the behavior of Semantic Web services and to capture provenance of computed attributes.

A parameter [SIO\_000144](http://semanticscience.org/resource/SIO_000144) is a data item whose value changes the characteristics of a system or a function.

Parameters are attributes for a given software :

```
'BLAST parameter'
 equivalentClass
 'parameter' and 'is attribute of' some 'BLAST software'
```

if the software application has a number of parameters, we represent these as [collections](ODPCollection.md) of data items. For instance, we can represent the set of BLAST parameters as a collection of data items:

```
'BLAST parameters'
 equivalentClass
 'Collection'
 and 'has member' min 0 ('expect value' and 'has value' some float)
 and 'has member' min 0 ('database' and 'has value' some string)
 and 'has member' min 0 ('low complexity filter' and 'has value' some bool)
 and 'is attribute of' some 'BLAST software'
```