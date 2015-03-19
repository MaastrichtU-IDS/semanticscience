Measurements are at the core of science. The following specifies which types and relations can be used to express quantities and their units.

Quantities have specific values that should be specified using the 'has value' datatype property and the value restricted to a set of datatypes supported by [OWL](http://www.w3.org/TR/owl2-syntax/#Datatype_Maps) including owl:real, xsd:double, xsd:float, xsd:integer. Units can be specified using the [unit ontology](http://bioportal.bioontology.org/visualize/45500) with the 'has unit' object property. Quantities are the result of a measurement process, and as such can also be time indexed to a time instant or time interval (which itself is an object that specified as an xsd:dateTime). Finally, quantities are an attribute of the entity that was measured.

```
'quantity'
subClassOf
 'has value' some Literal  # consider owl:real (xsd:float, xsd:double, xsd:int, xsd:long)
  and 'has unit' only 'measurement unit'
  and 'is output of' only 'measurement process'
  and 'is attribute of' some 'entity'
  and 'measured at' some ('time instant' or 'time interval' and 'has value' some xsd:dateTime) #optional 
```

Thus, entities can be described in terms of their quantified attributes as follows:
```
'entity' 
subClassOf
  'has attribute' some (
    'quantity' 
    that 'has value' some Literal 
    and 'has unit' some 'measurement unit'
   )
```

Sometimes, it is desirable to express that the value of a part of an entity:
```
'measurement of x' 
subClassOf
  'quantity'
  'has value' some Literal 
  and 'has unit' some 'measurement unit'
  and 'is attribute of' some (
    'object'
    and 'is part of' some 'object'
  )
```





Finally, we can represent the generation of a quantity as follows:
```
'measuring process'
subClassOf 
 'process' 
 and 'has agent' some 'object'  # the agent (person, software, etc) initiating the measurement
 and 'has target' some ('has capability' some 'to be measured') # the entity being measured
 and 'has output' some 'quantity' # the measurement (see above)
 and 'has attribute' some 'time interval' # the time at which the measuring took place
 and 'has participant' some (object and 'has function' some 'to measure') # the device used to undertake the measurement, if any and 'conforms to' some 'effective specification' # a the protocol followed, if any
```