#!/usr/bin/env python3
"""Compare two OWL ontology versions and report differences."""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import DC, DCTERMS, OWL, RDF, RDFS, SKOS, XSD

SIO = "http://semanticscience.org/resource/"

# Well-known namespace prefixes for readable predicate display
_PREFIXES = [
    ("owl",     "http://www.w3.org/2002/07/owl#"),
    ("rdf",     "http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
    ("rdfs",    "http://www.w3.org/2000/01/rdf-schema#"),
    ("xsd",     "http://www.w3.org/2001/XMLSchema#"),
    ("skos",    "http://www.w3.org/2004/02/skos/core#"),
    ("dct",     "http://purl.org/dc/terms/"),
    ("dc",      "http://purl.org/dc/elements/1.1/"),
    ("sio",     "http://semanticscience.org/resource/"),
    ("vann",    "http://purl.org/vocab/vann/"),
    ("cito",    "http://purl.org/spar/cito/"),
    ("schema",  "http://schema.org/"),
    ("void",    "http://rdfs.org/ns/void#"),
    ("foaf",    "http://xmlns.com/foaf/0.1/"),
]


def curie(uri: str) -> str:
    for prefix, ns in _PREFIXES:
        if uri.startswith(ns):
            return f"{prefix}:{uri[len(ns):]}"
    local = uri.rsplit("/", 1)[-1].rsplit("#", 1)[-1]
    return local or uri

ENTITY_TYPES = {
    OWL.Class: "Class",
    OWL.ObjectProperty: "ObjectProperty",
    OWL.DatatypeProperty: "DatatypeProperty",
    OWL.AnnotationProperty: "AnnotationProperty",
    OWL.NamedIndividual: "Individual",
}

# Predicates tracked for per-entity change reporting
TRACKED_PREDICATES = {
    RDFS.label: "label",
    RDFS.comment: "comment",
    RDFS.seeAlso: "seeAlso",
    OWL.deprecated: "deprecated",
    DCTERMS.description: "dct:description",
    DC.description: "dc:description",
    DCTERMS.alternative: "dct:alternative",
    SKOS.definition: "skos:definition",
    SKOS.example: "skos:example",
    SKOS.exactMatch: "skos:exactMatch",
    SKOS.closeMatch: "skos:closeMatch",
    URIRef(SIO + "equivalentTo"): "sio:equivalentTo",
    URIRef(SIO + "similarTo"): "sio:similarTo",
    RDFS.subClassOf: "subClassOf",
    RDFS.subPropertyOf: "subPropertyOf",
    OWL.equivalentClass: "equivalentClass",
    OWL.equivalentProperty: "equivalentProperty",
    RDFS.domain: "domain",
    RDFS.range: "range",
    OWL.inverseOf: "inverseOf",
    OWL.disjointWith: "disjointWith",
}


def load_graph(path: str) -> Graph:
    g = Graph()
    g.parse(path)
    return g


def label_for(g: Graph, node) -> str:
    if isinstance(node, URIRef):
        lbl = g.value(node, RDFS.label)
        if lbl:
            return str(lbl)
        local = str(node).rsplit("/", 1)[-1].rsplit("#", 1)[-1]
        return local
    return str(node)


def get_entities(g: Graph) -> dict:
    """Return {uri: type_name} for all named (non-blank) entities."""
    entities = {}
    for entity_type, type_name in ENTITY_TYPES.items():
        for s in g.subjects(RDF.type, entity_type):
            if isinstance(s, URIRef):
                entities[s] = type_name
    return entities


def object_values(g: Graph, subject: URIRef, predicate) -> set:
    """All non-blank-node objects for a subject/predicate pair."""
    return {o for o in g.objects(subject, predicate) if not isinstance(o, BNode)}


def compare_entity(uri: URIRef, g1: Graph, g2: Graph) -> list[tuple[str, str, str]]:
    """
    Return list of (change, predicate_name, value_str) for a modified entity.
    change is '+' (added) or '-' (removed).
    """
    changes = []
    for pred, pred_name in TRACKED_PREDICATES.items():
        vals1 = object_values(g1, uri, pred)
        vals2 = object_values(g2, uri, pred)
        for v in sorted(vals2 - vals1, key=str):
            changes.append(("+", pred_name, label_for(g2, v)))
        for v in sorted(vals1 - vals2, key=str):
            changes.append(("-", pred_name, label_for(g1, v)))
    return changes


def get_ontology_uri(g: Graph) -> URIRef | None:
    return next(g.subjects(RDF.type, OWL.Ontology), None)


def compare_ontology_annotations(g1: Graph, g2: Graph) -> list[dict]:
    """
    Compare all predicate-object pairs on the owl:Ontology node.
    Returns list of {op, predicate, value} dicts.
    """
    ont1 = get_ontology_uri(g1)
    ont2 = get_ontology_uri(g2)

    # Gather all (predicate, object) pairs, skipping rdf:type and blank nodes
    def annotation_pairs(g: Graph, ont: URIRef | None) -> set:
        if ont is None:
            return set()
        return {
            (p, o)
            for p, o in g.predicate_objects(ont)
            if p != RDF.type and not isinstance(o, BNode)
        }

    pairs1 = annotation_pairs(g1, ont1)
    pairs2 = annotation_pairs(g2, ont2)

    changes = []
    for p, o in sorted(pairs2 - pairs1, key=lambda x: (str(x[0]), str(x[1]))):
        changes.append({"op": "+", "predicate": curie(str(p)), "value": str(o)})
    for p, o in sorted(pairs1 - pairs2, key=lambda x: (str(x[0]), str(x[1]))):
        changes.append({"op": "-", "predicate": curie(str(p)), "value": str(o)})
    return changes


def build_diff(g1: Graph, g2: Graph) -> dict:
    entities1 = get_entities(g1)
    entities2 = get_entities(g2)
    all_uris = set(entities1) | set(entities2)

    result = defaultdict(lambda: {"added": [], "removed": [], "modified": []})

    for uri in all_uris:
        in1, in2 = uri in entities1, uri in entities2
        if in2 and not in1:
            type_name = entities2[uri]
            result[type_name]["added"].append({
                "uri": str(uri),
                "label": label_for(g2, uri),
            })
        elif in1 and not in2:
            type_name = entities1[uri]
            result[type_name]["removed"].append({
                "uri": str(uri),
                "label": label_for(g1, uri),
            })
        else:
            changes = compare_entity(uri, g1, g2)
            if changes:
                type_name = entities1[uri]
                result[type_name]["modified"].append({
                    "uri": str(uri),
                    "label": label_for(g1, uri),
                    "changes": [{"op": op, "predicate": p, "value": v} for op, p, v in changes],
                })

    # Sort each list for stable output
    for type_name, groups in result.items():
        groups["added"].sort(key=lambda x: x["label"].lower())
        groups["removed"].sort(key=lambda x: x["label"].lower())
        groups["modified"].sort(key=lambda x: x["label"].lower())

    return {
        "ontology": compare_ontology_annotations(g1, g2),
        "entities": dict(result),
    }


def print_text(diff: dict, path1: str, path2: str) -> None:
    ont_changes = diff["ontology"]
    entities = diff["entities"]

    total_added = sum(len(g["added"]) for g in entities.values())
    total_removed = sum(len(g["removed"]) for g in entities.values())
    total_modified = sum(len(g["modified"]) for g in entities.values())

    print(f"{'='*64}")
    print(f"Ontology Diff")
    print(f"  v1: {path1}")
    print(f"  v2: {path2}")
    print(f"{'='*64}")
    print(f"  {len(ont_changes)} ontology annotation change(s)")
    print(f"  {total_added} added  |  {total_removed} removed  |  {total_modified} modified\n")

    if not ont_changes and not entities:
        print("No differences found.")
        return

    if ont_changes:
        print(f"## Ontology Annotations  (~{len(ont_changes)})\n")
        for c in ont_changes:
            # Truncate long values (e.g. contributor lists) for readability
            value = c["value"].replace("\n", " ").strip()
            if len(value) > 120:
                value = value[:117] + "..."
            print(f"  {c['op']} {c['predicate']}: {value}")
        print()

    for type_name in sorted(entities):
        groups = entities[type_name]
        n_a, n_r, n_m = len(groups["added"]), len(groups["removed"]), len(groups["modified"])
        if not (n_a or n_r or n_m):
            continue

        print(f"## {type_name}  (+{n_a} / -{n_r} / ~{n_m})")

        if groups["added"]:
            print(f"\n  ADDED ({n_a}):")
            for e in groups["added"]:
                print(f"    + {e['label']}")
                print(f"      {e['uri']}")

        if groups["removed"]:
            print(f"\n  REMOVED ({n_r}):")
            for e in groups["removed"]:
                print(f"    - {e['label']}")
                print(f"      {e['uri']}")

        if groups["modified"]:
            print(f"\n  MODIFIED ({n_m}):")
            for e in groups["modified"]:
                print(f"    ~ {e['label']}")
                print(f"      {e['uri']}")
                for c in e["changes"]:
                    print(f"      {c['op']} {c['predicate']}: {c['value']}")

        print()


def print_json(diff: dict, path1: str, path2: str) -> None:
    entities = diff["entities"]
    output = {
        "v1": path1,
        "v2": path2,
        "summary": {
            "ontology_annotation_changes": len(diff["ontology"]),
            "added": sum(len(g["added"]) for g in entities.values()),
            "removed": sum(len(g["removed"]) for g in entities.values()),
            "modified": sum(len(g["modified"]) for g in entities.values()),
        },
        "diff": diff,
    }
    print(json.dumps(output, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Compare two OWL ontology versions and report differences."
    )
    parser.add_argument("ontology1", help="Path or URL of the first (older) ontology")
    parser.add_argument("ontology2", help="Path or URL of the second (newer) ontology")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)"
    )
    args = parser.parse_args()

    print(f"Loading {args.ontology1} ...", file=sys.stderr)
    g1 = load_graph(args.ontology1)
    print(f"Loading {args.ontology2} ...", file=sys.stderr)
    g2 = load_graph(args.ontology2)

    diff = build_diff(g1, g2)

    if args.format == "json":
        print_json(diff, args.ontology1, args.ontology2)
    else:
        print_text(diff, args.ontology1, args.ontology2)


if __name__ == "__main__":
    main()
