#!/usr/bin/env python3
"""Whole-ontology satisfiability regressions for issue #109 (Java + HermiT).

No imports, axioms or declarations are removed from the input ontology. Negated
existentials explicitly close the property for the tested element; missing
triples alone would not establish absence under OWL's open-world semantics.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

from rdflib import BNode, Graph, Literal, Namespace, RDF, RDFS, OWL
from rdflib.collection import Collection

ROOT = Path(__file__).resolve().parents[1]
T = Namespace("urn:sio:issue109:")
DEFAULTS = [
    "ontology/sio.owl",
    "ontology/sio/release/sio-release.owl",
    "ontology/sio/release/sio-subset-camelcase-label.owl",
    "ontology/sio/release/sio-subset-dash-labels.owl",
    "ontology/sio/release/sio-subset-labels.owl",
]


def check(path, jar, baseline=False):
    g = Graph().parse(path)
    # Resolve labels to support both numeric and label-URI serializations.
    def term(label):
        matches = list(g.subjects(RDFS.label, Literal(label, lang="en")))
        assert len(matches) == 1, (path, label, matches)
        return matches[0]

    def some(prop, filler):
        n = BNode()
        for p, o in [(RDF.type, OWL.Restriction), (OWL.onProperty, prop),
                     (OWL.someValuesFrom, filler)]:
            g.add((n, p, o))
        return n

    def complement(expr):
        n = BNode()
        g.add((n, RDF.type, OWL.Class))
        g.add((n, OWL.complementOf, expr))
        return n

    def intersection(*members):
        n, head = BNode(), BNode()
        g.add((n, RDF.type, OWL.Class))
        g.add((n, OWL.intersectionOf, head))
        Collection(g, head, members)
        return n

    part, part_of = term("has part"), term("is part of")
    sub, organic = term("organic submolecule"), term("organic molecule")
    oxygen = some(part, term("oxygen atom"))
    carbon = some(part, term("carbon atom"))
    hydrogen = some(part, term("hydrogen atom"))
    probes = {
        "SubmoleculeWithoutOxygen": (intersection(sub, complement(oxygen)), not baseline),
        "SubmoleculeWithOxygen": (intersection(sub, oxygen), True),
        "SubmoleculeWithoutCarbon": (intersection(sub, complement(carbon)), False),
        "SubmoleculeWithoutOrganicHost": (
            intersection(sub, complement(some(part_of, organic))), False),
        "MoleculeWithoutOxygen": (intersection(organic, complement(oxygen)), True),
        "MoleculeWithOrganicPartWithoutOxygen": (
            intersection(organic, some(part, sub), complement(oxygen)), not baseline),
        "OrganicPolymerWithoutOxygen": (
            intersection(term("organic polymer"), complement(oxygen)), not baseline),
        "MoleculeWithoutCarbon": (intersection(organic, complement(carbon)), False),
        # Preserve existing scope in this narrowly targeted fix; see investigation.
        "MoleculeWithoutHydrogen": (intersection(organic, complement(hydrogen)), False),
        # Necessary elemental conditions must not become a sufficient definition.
        "CarbonHydrogenMoleculeNotOrganic": (
            intersection(term("molecule"), carbon, hydrogen, complement(organic)), True),
    }
    for name, (expr, _) in probes.items():
        g.add((T[name], RDF.type, OWL.Class))
        g.add((T[name], OWL.equivalentClass, expr))
    with tempfile.TemporaryDirectory(prefix="sio-issue109-") as tmp:
        augmented = Path(tmp) / "probes.owl"
        g.serialize(augmented, format="xml")
        cmd = ["java", "-Xmx2G", "-cp", str(jar),
               "org.semanticweb.HermiT.cli.CommandLine", "-k"]
        cmd += [f"-k<{T[name]}>" for name in probes]
        cmd.append(augmented.as_uri())
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    assert "http://www.w3.org/2002/07/owl#Thing is satisfiable." in result.stdout, result.stdout
    for name, (_, expected) in probes.items():
        expected_line = f"<{T[name]}> is {'satisfiable' if expected else 'not satisfiable'}."
        assert expected_line in result.stdout.splitlines(), (path, expected_line, result.stdout)
    print(f"PASS {path}: ontology consistent; {len(probes)} satisfiability checks", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--hermit-jar", type=Path)
    parser.add_argument("--expect-original-defect", action="store_true",
                        help="Expect the three oxygen-free submolecule/host/polymer probes to fail")
    args = parser.parse_args()
    if args.hermit_jar:
        jar = args.hermit_jar
    else:
        import owlready2
        jar = Path(owlready2.__file__).parent / "hermit" / "HermiT.jar"
    if not jar.is_file():
        parser.error(f"HermiT JAR not found: {jar}")
    for path in args.paths or [ROOT / name for name in DEFAULTS]:
        check(path.resolve(), jar.resolve(), args.expect_original_defect)


if __name__ == "__main__":
    main()
