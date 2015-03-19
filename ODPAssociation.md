An association is a relationship between two or more entities.

```
'association'
subClassOf
 'mathematical entity'
 and 'refers to' min 2 entity
```

Thus, a gene-disease association is an association between a gene and a disease

```
'gene-disease association'
subClassOf
 'association'
 and 'refers to' some gene
 and 'refers to' some disease
```

An association may be the result of some experiment and have a particular confidence value associated with it, or may be reported in some document:

```
subClassOf
 'is product of' some 'experiment'
 and 'has attribute' some ('probability measure' that 'has value' some double)
 and 'has source' some 'document'
```


statistical association as an association/relationship in which the significance is quantified through some statistic (e.g. probability value)

```
'statistical association'
subClassOf
 'association'
  and 'refers to' min 2 'entity'
  and 'has measurement value' some ('quantity' or 'probability value')
  and 'is model of' some 'entity'
```

optionally, the statistical association can be a model for some entity or more specifically, process.  The unit of a measurement value can can be specified using the [unit ontology](http://bioportal.bioontology.org/visualize/45500) with the sio:has-unit object property.