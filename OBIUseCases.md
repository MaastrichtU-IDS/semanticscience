# Use Cases #

https://docs.google.com/document/d/11G4EkYvGJSJfcgW98weOyo5iVr7TdmrWEhm_q2IeGrA/edit

using the simple triples syntax

1. mass of patient recorded at 74.5 kilograms
```
sio: <http://semanticscience.org/resource/>
taxon : <http://bio2rdf.org/taxon:>
obo: <http://purl.obolibrary.org/obo/>

:p a taxon:9606 .                      # p is human
:p sio:has-attribute :m1 .             # p has an attribute of m1

:m1 a sio:mass .                       # m1 is a mass
:m1 sio:has-value "74.5"^^xsd:float .  # the value is 74.6
:m1 sio:has-unit obo:UO_0000009 .      # the unit is kilogram
```

2. prescribed 150mg of aspirin [twice a day for 3 days ](.md)
```
sio: <http://semanticscience.org/resource/>
drugbank: <http://bio2rdf.org/drugbank:>
obo: <http://purl.obolibrary.org/obo/>

#describe the prescription event
:e a sio:medical-procedure .           # e is a medical procedure as defined by SIO
:e a snomedct:16076005 .               # e prescription as defined by snomed-ct
:e sio:realizes [ a :prescriptee-role; sio:is-role-of :pat ] .   # in this event, the patient plays the role of the prescriptee
:e sio:realizes [ a :prescriptor-role; sio:is-role-of :doc ] .   # in this event, the doctor plays the role of the prescriptor
:e sio:has-output :s.                  # the prescription event produces a script

:s a :script .                         # s is the script
:s sio:specifies :f .                  # the script specifies the frequency of administration
:s sio:specifies :d .                  # the script specifies the drug
:s sio:specifies :q .                  # the script specifies the quantity

:f a :frequency-of-administration .    # f is the frequency of administration 
:f sio:has-value "12"^^xsd:integer .   # every 12 hours 
:f sio:has-unit obo:UO_0000032 .       # hours

:d a :heterogeneous-substance .        # d is a pharmaceutical substance as defined by SIO
:d a drugbank:DB00945 .                # d is aspirin as defined by drugbank
:d sio:has-component-part :c .         # d is composed of c
:c a obo:CHEBI_15365 .                 # c is the chemical entity as defined by chebi

:q a sio:dose .                        # q is a quantity of drug as defined by SIO
:q sio:has-value "150.0"^^xsd:float .  # q has a value of 150.0
:q sio:has-unit obo:UO_0000022 .       # q has unit of mg
:q sio:is-attribute-of :d .            # q is an attribute of d

```

3. reporting an a dimensional quantity (a count): 10 petals of a flower
```
sio: <http://semanticscience.org/resource/>
obo: <http://purl.obolibrary.org/obo/>

:c a sio:count .                       # c is a count as defined by SIO
:c sio:has-value "10"^^xsd:integer .   # c has value of 10
:c sio:is-attribute-of :f .            # c is an attribute of f
:f a obo:PO_0009046 .                  # f is a flower as defined by the plant ontology
```


4. reporting a categorical variable (a quality with several possible values): handedness, colour of eyes, dose of aspirin (high dose, low dose)

```
sio: <http://semanticscience.org/resource/>
obo: <http://purl.obolibrary.org/obo/>
fma: <http://sig.uw.edu/fma#>

:i a owl:NamedIndividual .
:i sio:has-quality obo:PATO_0002203 .  # individual is right handed
:i sio:has-direct-part :e1, e2.        # individual has two eyes
:e1 a fma:eye                          # e1 is an eye as defined by FMA
:e1 sio:has-quality obo:PATO_0000318 . # blue
:e2 a fma:eye                          # e1 is an eye as defined by FMA
:e1 sio:has-quality obo:PATO_0000952.  # brown
```


5. reporting the duration of a process  (e.g. 15 minutes)

```
sio: <http://semanticscience.org/resource/>
obo: <http://purl.obolibrary.org/obo/>

:p a sio:process .                     # p is a process as defined by SIO
:p sio:has-attribute :d .              # p has an attribute d
:d a sio:time-interval .               # d is a time interval
:d sio:has-value "15.0"^^xsd:float .   # d has a value of 15
:d sio:has-unit obo:UO_0000031 .       # d's value is in minutes (see also sio:minute)
```

6. reporting the date a process occurred
```
sio: <http://semanticscience.org/resource/>
obo: <http://purl.obolibrary.org/obo/>

:p a sio:process .                     # p is a process as defined by SIO
:p sio:has-attribute :d1, :d2 .        # p has an attribute d1 and d2
:d1 a sio:start-date .                 # d1 is a process start date
:d1 sio:has-value "2012-01-15T12:00:00-05:00"^^xsd:dateTime .  # the value of the start date is January 15, 2012 at 12PM EDT
:d2 a sio:end-date .                   # d2 is a process end date
:d2 sio:has-value "2013-01-15T12:00:00-05:00"^^xsd:dateTime .  # the value of the end date is January 15, 2013 at 12PM EDT

```