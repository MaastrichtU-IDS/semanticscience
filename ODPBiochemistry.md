# Biochemical Pathway #
A biochemical pathway specifies of a set of connected biochemical events, in which some involve the formation/dissociation of complexes (and any subsequently conformational changes) and others involve (bio)chemical transformations. The first and most naive representation ignores bioenergetics and simply represents the pathway as a set of biotransformations.

Let's look at glycolysis as an example, where we have an ordered set of reactions:

```
'glycolysis' equivalentTo:
'pathway'
 and 'has proper part' some ('hexokinase reaction' and 'precedes' some ('phosphoglucose isomerase reaction' and 'precedes' ...)
 and 'has proper part' some 'hexokinase reaction'
 and 'has proper part' some 'phosphoglucose isomer reaction'
 ....
```

now if we take a look at a specific reaction such as the hexokinase one (in glycolysis), we state
```
'hexokinase'
'biochemical reaction'
and 'realizes' some ('reactant role' that 'is role of' some 'glucose')
and 'realizes' some ('reactant role' that 'is role of' some 'ATP')
and 'realizes' some ('catalytic role' that 'is role of' some 'hexokinase')
and 'realizes' some ('product role' that 'is role of' some 'glucose-6-phosphate'
and 'realizes' some ('product role' that 'is role of' some 'ADP')
```



# Enzyme Mechanism #

Consider an ordered sequential reaction (bi-bi) between an enzyme and a substrate (e.g. hexokinase)

```
'ATP-enzyme complex formation' equivalentTo:
'complex formation'
and 'realizes' some ('to be part of' and 'is disposition of' some 'enzyme' and 'in relation to' some 'ATP-enzyme complex')
and 'realizes' some ('to be part of' and 'is disposition of' some 'ATP' and 'in relation to' some 'ATP-enzyme complex')

'ATP-substrate-enzyme complex formation' equivalentTo:
'complex formation'
and 'realizes' some ('to be part of' and 'is disposition of' some 'ATP-enzyme complex' and 'in relation to' some 'ATP-substrate-enzyme complex' )
and 'realizes' some ('to be part of' and 'is disposition of' some 'ATP' and 'in relation to' some 'ATP-substrate-enzyme complex')

'substrate-enzyme phosphorylation by ATP' equivalentTo:
'biochemical reaction'
and 'realizes' some ('substrate role' and 'is role of' some 'ATP-substrate enzyme complex')
and 'realizes' some ('product role' and 'is role of' some 'ADP-substrate-phosphorylated-enzyme complex')


'ADP dissociation from phosphorylated-enzyme substrate complex' equivalentTo:
'complex dissociation'
and 'realizes' some ('to dissociate' and 'is disposition of' some 'phosphorylated-enzyme-substrate complex' and 'in relation to' some 'ADP-substrate-phosphorylated-enzyme complex' )
and 'realizes' some ('to dissociate' and 'is disposition of' some 'ADP' and 'in relation to' some 'ADP-substrate-phosphorylated-enzyme complex')

'substrate-phosphorylation by phosphorylated enzyme' equivalentTo:
'biochemical reaction'
and 'realizes' some ('substrate role' and 'is role of' some 'substrate-phosphorylated-enzyme complex')
and 'realizes' some ('product role' and 'is role of' some 'phosphorylated-substrate-enzyme complex')

'dissociation of phosphorylated substrate from phosphorylated-substrate-enzyme complex' equivalentTo:
'complex dissociation'
and 'realizes' some ('to dissociate' and 'is disposition of' some 'phosphorylated-substrate' and 'in relation to' some 'phosphorylated-substrate-enzyme complex' )
and 'realizes' some ('to dissociate' and 'is disposition of' some 'enzyme' and 'in relation to' some 'phosphorylated-substrate-enzyme complex')


```