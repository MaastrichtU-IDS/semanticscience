# Semanticscience Integrated Ontology (SIO)

SIO provides a simple, integrated ontology of types and relations for rich description of objects, processes, and their attributes. See the [overview](https://github.com/micheldumontier/semanticscience/wiki/SIO-Overview), [design principles](https://github.com/micheldumontier/semanticscience/wiki/Ontology-Design-Principles), [design patterns](https://github.com/micheldumontier/semanticscience/wiki/Design-Patterns), and the published [paper](http://www.jbiomedsem.com/content/5/1/14).

## Ontology

The OWL2 ontology is available at http://semanticscience.org/ontology/sio.owl

Subsets are available for modular import:
- [Labels as SIO URIs](https://github.com/micheldumontier/semanticscience/tree/master/ontology/sio/release/sio-subset-labels.owl)
- [All subsets (core, chemical, nlp, etc.)](https://github.com/micheldumontier/semanticscience/tree/master/ontology/sio/release/)

Browse the ontology:
- [BioPortal](http://bioportal.bioontology.org/ontologies/SIO)
- [Ontobee](https://ontobee.org/ontology/SIO)
- [AgroPortal](https://agroportal.lirmm.fr/ontologies/SIO)
- [AberOWL](http://aber-owl.net/ontology/SIO)

SIO term resolution is handled by Ontobee:
- [protein — SIO_010043](http://semanticscience.org/resource/SIO_010043)
- [dataset — SIO_000089](http://semanticscience.org/resource/SIO_000089)
- [data analysis — SIO_001051](http://semanticscience.org/resource/SIO_001051)

## Community

Questions: [sio-ontology mailing list](http://groups.google.com/group/sio-ontology) (sio-ontology@googlegroups.com)  
Term requests: [issue tracker](https://github.com/micheldumontier/semanticscience/issues)

Projects using SIO:
- [Bio2RDF](http://bio2rdf.org/) — Linked Data for the Life Sciences
- [SADI Semantic Web Services](http://sadiframework.org)
- [DisGeNET](http://rdf.imim.es/DisGeNET.html) — gene-disease associations
- [PubChem RDF](http://pubchem.ncbi.nlm.nih.gov/rdf/) (NCBI) — measurement values
- [Gene Expression Atlas](http://www.ebi.ac.uk/rdf/documentation/atlas) (EBI)
- [Graph4Code](https://wala.github.io/graph4code/)
- [IDSM](https://academic.oup.com/bioinformatics/advance-article/doi/10.1093/bioinformatics/btae174/7638802) — Integrated Database of Small Molecules

## Development

### Setup

Python 3.8+ is required.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Scripts

#### `scripts/bump_version.py` — Increment the ontology version

Updates `owl:versionInfo` in `ontology/sio.owl` and sets `dct:modified` to today's date.

```bash
python3 scripts/bump_version.py            # bump minor version (default): 1.59 -> 1.60
python3 scripts/bump_version.py --major    # bump major version:           1.59 -> 2.0
python3 scripts/bump_version.py --patch    # bump patch version:           1.59 -> 1.59.1
python3 scripts/bump_version.py --set 2.0  # set an explicit version
python3 scripts/bump_version.py --dry-run  # preview without writing
```

#### `scripts/generate_subsets.py` — Generate subset OWL files

Reads `ontology/sio.owl` and writes subset files to `ontology/sio/release/`. Replaces `ontology/generatesubsets.php`.

```bash
python3 scripts/generate_subsets.py
```

Output files:

| File | Description |
|------|-------------|
| `sio-subset-<name>.owl` | Per-subset ontology derived from `sio:subset` annotations |
| `sio-subset-camelcase-label.owl` | All terms with URIs derived from camelCase labels |
| `sio-subset-dash-labels.owl` | All terms with URIs derived from dash-separated labels |
| `sio-subset-labels.owl` | Copy of `sio-subset-dash-labels.owl` |
| `sio-release.owl` | Full versioned release with `rdfs:isDefinedBy` and `owl:versionIRI` |

Subset membership is controlled by the `sio:subset` annotation property. The value supports suffix modifiers:

| Suffix | Meaning |
|--------|---------|
| `name` | Include this term only |
| `name+` | Include this term and all descendants (transitive `rdfs:subClassOf`) |
| `name++` | Include this term, all descendants, and all ancestors |
| `name-` | Exclude this term and all descendants |

#### `scripts/diff_ontologies.py` — Compare two ontology versions

Reports ontology-level annotation changes and added, removed, or modified classes, properties, and individuals between two OWL files.

```bash
python3 scripts/diff_ontologies.py <ontology1> <ontology2> [--format text|json]
```

- Inputs can be local file paths or URLs
- Default output is human-readable text; `--format json` produces machine-readable output
- Tracks: labels, definitions (`dct:description`), comments, deprecation, synonyms, `subClassOf`, `equivalentClass`, `domain`, `range`, `inverseOf`, `disjointWith`, and more

```bash
# Compare working file against a previous release
python3 scripts/diff_ontologies.py ontology/sio.owl ontology/sio/release/sio-release.owl

# Save diff as JSON
python3 scripts/diff_ontologies.py ontology/sio.owl ontology/sio-new.owl --format json > diff.json
```
