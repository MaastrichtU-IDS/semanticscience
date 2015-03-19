Databases act as containers for informational entities (tokens)

```
'informational entity'
  'is about' only 'entity'
```

```
'database' 
 subClassOf 
  'informational entity'
  and 'has component part' only 'table'
```

```
'table'
 subClassOf
 'informational entity'
  and 'has proper part' min 1 'column'
  and 'has proper part' min 0 row
  and 'is part of' min 1 database
```

```
'column'
 subClassOf 
  'informational entity'
  and 'has attribute' min 1 ('name' that 'has value' some string)
  and 'specifies' only (
        'cell'
          and 'has value' some literal 
          and 'has value' only literal)
  and 'is proper part of' some 'table'
```

```
'row'
 subClassOf 
  'informational entity'
  and 'has proper part' min 1 'cell'
  and 'is proper part of' some 'table'
```

```
'cell'
 subClassOf
  'informational entity'
  and 'has value' some literal
  and 'is proper part of' some 'row'
  and 'is specified by' some 'column'
```

```
'unique column'  
 subClassOf 
  'column' and 'specifies' only 'unique cell'
```

```
'unique cell'
 subClassOf
  'cell' and 'has unique identifier' some 'identifier'
```

```
'has unique identifier'
 subPropertyOf 'has identifier'
   a owl:InverseFunctionalProperty
```

```
'is unique identifier of'
  a owl:InverseProperty
```

```
'referencing cell'
 subClassOf
  'cell' and 'refers to' some cell
```

```
'referent cell'
 subClassOf
  'cell' and 'is referred to by' some cell
```

```
'database key'
 rdfs:label 'An informational entity composed of columns that may constrain the values of cells in every row of a table'
 subClassOf
  'informational entity'
  and 'has component part' some 'column'
  and 'is proper part' some 'table'
  and 'has value' some literal
```

```
'database primary key'
 rdfs:label "Database key that identifies every row of a table."
 subClassOf
  'database key'
  and 'is unique identifier for' some 'row'
  and not('has value' value "null")
```

```
'database foreign key'
 rdfs:label "Database key that references a key."
 subClassOf
  'database key'
  and 'references' some 'database key'
```