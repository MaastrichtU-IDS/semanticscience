# Issue #109: oxygen requirement in organic submolecules

Investigated against master `a792b59bf23b5971c20fcb9aa0ee7e648d04f6b7`
(SIO 1.62), 16 October 2026.

## Finding and exact axioms

The report identifies a real asserted restriction, but the subject of its final
quoted axiom should be **organic submolecule**, not organic molecule.
The source `ontology/sio.owl` and full release
`ontology/sio/release/sio-release.owl` assert these necessary conditions
(Manchester syntax; labels stand for the IDs below):

```manchester
Class: 'organic submolecule'  # SIO_010071
  SubClassOf:
    'submolecule',           # SIO_010441
    'is part of' some 'organic molecule',
    ('has part' some 'carbon atom') and ('has part' some 'oxygen atom')

Class: 'organic molecule'    # SIO_010072
  SubClassOf:
    'molecule',              # SIO_011125
    ('has part' some 'carbon atom') and ('has part' some 'hydrogen atom')
```

Properties: has part = SIO_000028; is part of = SIO_000068.
Atoms: carbon = SIO_011001; hydrogen = SIO_011002; oxygen = SIO_011007.
These are subclass axioms, not equivalent-class definitions.
`ontology/sio-dev.owl` explicitly directs changes to `sio.owl` and imports it;
it contains no overriding definition of either class.

The source uses separate RDF/XML blank-node descriptions for the intersection,
RDF list and restrictions. Reading only the named class block misses the content
of those expressions. The chemical subset omits them entirely:
`scripts/generate_subsets.py` skips triples with a blank-node object when building
ordinary subsets. It is therefore an intentionally reduced representation, not
evidence against the restriction in the source. The full release and the three
label-URI files preserve the restriction.

## Entailments and chemical interpretation

The oxygen existential on organic submolecule is explicit. Furthermore,
`has part` is transitive and inverse to `is part of`. An organic molecule with
an organic submolecule therefore has an oxygen part. The existing organic polymer
class (SIO_010346) requires an organic submolecule part and consequently inherits
the oxygen requirement. This does **not** imply that every organic molecule has
oxygen: not every organic molecule is required to have an organic submolecule.
The existential organic host can be distinct from a separately asserted host;
it must not be assumed to identify that host without additional evidence.

Oxygen is not required in organic chemistry: IUPAC defines hydrocarbons using
carbon and hydrogen only. PDBe records beta-carotene as C40H56. ChEBI records
poly(isoprene) macromolecules as (C5H8)n. Thus the restriction is scientifically
wrong, independently of the reporter's final subject typo. An isoprene-derived
unit within a molecule should be distinguished from a separate free isoprene
molecule; the counterexample needs only an oxygen-free carbon-containing region,
not a commitment about eight independently existing isoprene molecules.

The current submolecule annotation merely describes a connected region of a
molecule. It neither mentions the carbon condition nor specifies an organic
host. A possible clarified wording is: "An organic submolecule is a
carbon-containing connected region of an organic molecule." This describes the
retained carbon-containing interpretation; it does not mean every region of an
organic molecule is carbon-containing. If the intended scope includes any region
(e.g. a hydroxyl group alone), the carbon condition also needs a separate scope
decision. No annotation wording is changed by this narrowly scoped correction.

The organic molecule annotation's phrase "organic atoms" is imprecise: an
individual carbon or hydrogen atom is not intrinsically organic. Its mandatory
hydrogen condition is also too narrow for the usual broad chemical scope:
tetrachloromethane (CCl4) is a chlorocarbon with no hydrogen. ChEBI's organic
molecule definition requires carbon without requiring hydrogen. The existing
SIO hydrogen axiom and annotation should be reviewed together in a separate
scope change; the regression explicitly preserves current behavior rather than
presenting that condition as universally correct chemistry.

## Minimal correction

Replace only the carbon-and-oxygen intersection for SIO_010071 with:

```manchester
'organic submolecule' SubClassOf 'has part' some 'carbon atom'
```

Retain its submolecule superclass and organic-host existential. Remove the four
now-unused blank nodes (intersection, two list cells, oxygen restriction).
Apply the identical change in the full release and the three label-URI files.
Do not regenerate every subset, change a version/date, or introduce unrelated
serialization churn in this repair. The chemical subset has no affected axiom.
Normal release generation can follow the maintainers' release process.

Oxygen becomes optional, not forbidden. Do not replace it with mandatory hydrogen:
a carbonyl region, for example, need not contain hydrogen.

OWL can express necessary carbon and parent membership conditions directly,
without punning, reification or extra upper-level classes. Optional elements
need no existential restriction. An allowed-elements universal restriction would
close chemical scope and exclude halogens/metals; it is not justified here.
A carbon-containing molecule is not automatically organic under every chemical
convention, so do not introduce an equivalence from elemental composition alone.
For a broader organic-molecule definition, keep scientifically valid necessary
conditions and curate membership rather than claiming a complete classifier.

Unbounded connectedness of an arbitrary induced molecular subgraph is not
captured by a generic has-part existential or transitive reachability property.
OWL can model bounded patterns and curated connected-region classes, but general
connectivity and completeness of an atom/bond graph require an explicit graph
representation and an external graph validation step. A formula or missing
oxygen triple alone also does not exclude oxygen under the open-world semantics.

## Reproduce the reasoning regression

Java is required. From the repository root:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r tests/requirements.txt
python tests/issue109_reasoning.py
```

The runner invokes the HermiT CLI bundled with Owlready2 0.49, loading each full
RDF/XML input directly through OWLAPI. It adds only temporary equivalent-class
probes. No source axioms, imports or declarations are filtered or removed.
An explicit complement of `has part some oxygen atom` tests oxygen absence;
absence is never inferred merely from missing assertions. These are abstract
chemical counterexample patterns, not full atom-count/connectivity models.

Each file is checked for ontology consistency and ten satisfiability outcomes:

| Probe | Original | Corrected |
|---|---|---|
| Organic submolecule without oxygen | Unsatisfiable | Satisfiable |
| Organic submolecule with oxygen | Satisfiable | Satisfiable |
| Organic submolecule without carbon | Unsatisfiable | Unsatisfiable |
| Organic submolecule without an organic host | Unsatisfiable | Unsatisfiable |
| Organic molecule without oxygen | Satisfiable | Satisfiable |
| Organic molecule with organic part, without oxygen | Unsatisfiable | Satisfiable |
| Organic polymer without oxygen | Unsatisfiable | Satisfiable |
| Organic molecule without carbon | Unsatisfiable | Unsatisfiable |
| Organic molecule without hydrogen | Unsatisfiable | Unsatisfiable |
| Carbon/hydrogen-containing molecule outside organic molecule | Satisfiable | Satisfiable |

The last row guards against accidentally converting necessary conditions into
an equivalent-class definition. `--expect-original-defect` checks the original
outcomes on a supplied original file; without that flag the original file must
fail the regression. `--hermit-jar PATH` allows an explicitly supplied HermiT JAR.
These are targeted regressions plus ontology consistency checks, not a claim
that every unrelated SIO class is satisfiable or chemically correct.

## Sources

- [Issue #109](https://github.com/MaastrichtU-IDS/semanticscience/issues/109)
- [Source at inspected commit](https://github.com/MaastrichtU-IDS/semanticscience/blob/a792b59bf23b5971c20fcb9aa0ee7e648d04f6b7/ontology/sio.owl)
- [Subset generator](https://github.com/MaastrichtU-IDS/semanticscience/blob/a792b59bf23b5971c20fcb9aa0ee7e648d04f6b7/scripts/generate_subsets.py)
- [IUPAC: hydrocarbons](https://goldbook.iupac.org/terms/view/H02889)
- [PDBe: beta-carotene](https://www.ebi.ac.uk/pdbe-srv/pdbechem/chemicalCompound/show/BCR)
- [ChEBI: poly(isoprene) macromolecule](https://www.ebi.ac.uk/chebi/CHEBI:53405)
- [ChEBI: tetrachloromethane](https://www.ebi.ac.uk/chebi/CHEBI:27385)
- [ChEBI: organic molecule](https://www.ebi.ac.uk/chebi/CHEBI:72695)
- [W3C OWL 2 Primer](https://www.w3.org/TR/owl2-primer/)
