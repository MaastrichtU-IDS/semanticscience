# Change #
There are many criterion for maintaining the identity of objects through time, of which [Ontoclean](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.99.7618&rep=rep1&type=pdf) is the most coherent, and philosophically agnostic.


We can represent the process of change as follows:
```
‘enzyme-catalyzed phosphorylation using ATP’
‘addition reaction’
and ‘has target’ some ‘protein’
and ‘has target’ some ‘ATP’
and ‘has agent’ some ‘phospho-enzyme’
and ‘has product’ some ‘phosphorylated protein’
and ‘has product’ some ‘ADP’
```

this implies that the protein is converted into a new molecular entity hence, we could make the instance-level assertion that

'protein' 'derives into' 'phosphorylated protein'
and
'ATP' 'derives into' 'ADP'

A more sophisticated approach takes into account the roles of these species.

```
‘enzyme-catalyzed phosphorylation using ATP’
‘addition reaction’
and ‘realizes’ some ('target role' that 'is role of' some ‘protein’)
and ‘realizes’ some ('target role' that 'is role of' some 'ATP')
and ‘realizes’ some ('catalytic role' that 'is role of' some ‘phospho-enzyme’)
and ‘realizes’ some ('product role' that 'is role of' some ‘phosphorylated protein’
and ‘realizes’ some ('product role' that 'is role of' some ‘ADP’)
```

in order to infer that these entities are participants in the process, we use a a role chain of the form
'realizes' o 'is role of' -> 'has participant'

note however, that we trade the more specific predicates that relate to agents, targets and products with the more general has participant relation, but that information is presented in the role.

