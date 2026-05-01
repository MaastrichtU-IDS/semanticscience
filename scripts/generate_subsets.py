#!/usr/bin/env python3
"""Generate SIO subset OWL files from sio.owl."""

import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote

from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, OWL, RDF, RDFS, XSD

VOID = Namespace("http://rdfs.org/ns/void#")
SIO_RES = Namespace("http://semanticscience.org/resource/")
SIO_ONT = URIRef("http://semanticscience.org/ontology/sio.owl")
SIO_SUBSET_PROP = SIO_RES.subset

EQUIV_MAP = {
    OWL.Class: OWL.equivalentClass,
    OWL.ObjectProperty: OWL.equivalentProperty,
    OWL.DatatypeProperty: OWL.equivalentProperty,
}

ROOT = Path(__file__).parent.parent
ONTOLOGY_DIR = ROOT / "ontology"
ODIR = ONTOLOGY_DIR / "sio" / "release"


def get_children(node, super_class_of, visited=None):
    if visited is None:
        visited = set()
    result = []
    if node in super_class_of and node not in visited:
        visited.add(node)
        for child in super_class_of[node]:
            result.append(child)
            result.extend(get_children(child, super_class_of, visited))
    return result


def get_parents(node, sub_class_of, visited=None):
    if visited is None:
        visited = set()
    result = []
    if node in sub_class_of and node not in visited:
        visited.add(node)
        for parent in sub_class_of[node]:
            result.append(parent)
            result.extend(get_parents(parent, sub_class_of, visited))
    return result


def make_camel_uri(label, is_property):
    camel = "".join(w.capitalize() for w in label.split())
    camel = camel.replace("(", "").replace(")", "")
    if is_property and camel:
        camel = camel[0].lower() + camel[1:]
    return str(SIO_RES) + quote(camel)


def make_dash_uri(label):
    return str(SIO_RES) + quote(label.replace(" ", "-"))


def main():
    sio_file = ONTOLOGY_DIR / "sio.owl"
    g = Graph()
    g.parse(str(sio_file))

    sio_version = str(g.value(SIO_ONT, OWL.versionInfo))
    version_iri = f"http://semanticscience.org/ontology/sio/v{sio_version}/sio-release.owl"

    camel_labels = {}   # str(subject) -> str(camelCase URI)
    dash_labels = {}    # str(subject) -> str(dash URI)
    sub_class_of = {}   # str(child) -> [str(parent), ...]
    super_class_of = {} # str(parent) -> [str(child), ...]
    subsets = {}        # str(subject) -> [subset_name, ...]

    for s, p, o in g:
        s_str = str(s)

        if p == RDFS.label and isinstance(o, Literal):
            label = str(o)
            types = set(g.objects(s, RDF.type))
            is_prop = OWL.ObjectProperty in types or OWL.DatatypeProperty in types
            camel_labels[s_str] = make_camel_uri(label, is_prop)
            dash_labels[s_str] = make_dash_uri(label)

        if p in (RDFS.subClassOf, RDFS.subPropertyOf) and isinstance(o, URIRef) and s != o:
            sub_class_of.setdefault(s_str, []).append(str(o))
            super_class_of.setdefault(str(o), []).append(s_str)

        if p == SIO_SUBSET_PROP:
            subsets.setdefault(s_str, []).append(str(o))

    # Process transitive-closure annotations (++, +, -)
    tree = {}  # name -> {'include': set, 'exclude': set}

    for s_str, subset_list in subsets.items():
        for subset_val in list(subset_list):
            if "++" in subset_val:
                name = subset_val[:-2]
                ie = tree.setdefault(name, {"include": set(), "exclude": set()})
                ie["include"].add(s_str)
                ie["include"].update(get_children(s_str, super_class_of))
                ie["include"].update(get_parents(s_str, sub_class_of))
                subset_list.remove(subset_val)
            elif "+" in subset_val:
                name = subset_val[:-1]
                ie = tree.setdefault(name, {"include": set(), "exclude": set()})
                ie["include"].add(s_str)
                ie["include"].update(get_children(s_str, super_class_of))
                subset_list.remove(subset_val)

            if "-" in subset_val and subset_val in subset_list:
                name = subset_val[:-1]
                ie = tree.setdefault(name, {"include": set(), "exclude": set()})
                ie["exclude"].add(s_str)
                ie["exclude"].update(get_children(s_str, super_class_of))
                subset_list.remove(subset_val)

    for name, ie in tree.items():
        for s_str in ie["include"] - ie["exclude"]:
            subsets.setdefault(s_str, []).append(name)

    # Build per-subset graphs with filtered triples
    subset_graphs = {}

    for s, p, o in g:
        s_str = str(s)
        if s_str not in subsets:
            continue

        for subset in subsets[s_str]:
            sg = subset_graphs.setdefault(subset, Graph())

            if subset == "sadi":
                if p not in (RDFS.subClassOf, RDFS.subPropertyOf):
                    sg.add((s, p, o))
                continue

            if isinstance(o, BNode):
                continue
            if isinstance(o, URIRef):
                o_str = str(o)
                if "owl" not in o_str and o_str in subsets:
                    if subset not in subsets[o_str]:
                        continue
            if subset == "relations" and p in (RDFS.domain, RDFS.range):
                continue

            sg.add((s, p, o))

    # Build equivalents graph (camelCase <-> dash <-> original URIs)
    equivs_g = Graph()
    for mapping in (camel_labels, dash_labels):
        for s_str, alt_uri in mapping.items():
            s = URIRef(s_str)
            alt = URIRef(alt_uri)
            for rdf_type in g.objects(s, RDF.type):
                if rdf_type in EQUIV_MAP:
                    equiv_rel = EQUIV_MAP[rdf_type]
                    equivs_g.add((s, equiv_rel, alt))
                    equivs_g.add((alt, equiv_rel, s))

    # Add dc:identifier to main graph
    for s in set(g.subjects()):
        if isinstance(s, URIRef):
            local_part = str(s).rsplit("/", 1)[-1]
            g.add((s, DC.identifier, Literal(local_part)))

    # Build camelcase-label graph: remap all URIs to camelCase equivalents
    camel_g = Graph()
    for s, p, o in g:
        s_node = URIRef(camel_labels.get(str(s), str(s))) if isinstance(s, URIRef) else s
        p_node = URIRef(camel_labels.get(str(p), str(p)))
        o_node = URIRef(camel_labels.get(str(o), str(o))) if isinstance(o, URIRef) else o
        camel_g.add((s_node, p_node, o_node))

    for s, p, o in equivs_g:
        s_node = URIRef(camel_labels.get(str(s), str(s))) if isinstance(s, URIRef) else s
        camel_g.add((s_node, p, o))

    # Build dash-labels graph: remap all URIs to dash equivalents
    dash_g = Graph()
    for s, p, o in g:
        s_node = URIRef(dash_labels.get(str(s), str(s))) if isinstance(s, URIRef) else s
        p_node = URIRef(dash_labels.get(str(p), str(p)))
        o_node = URIRef(dash_labels.get(str(o), str(o))) if isinstance(o, URIRef) else o
        dash_g.add((s_node, p_node, o_node))

    subset_graphs["camelcase-label"] = camel_g
    subset_graphs["dash-labels"] = dash_g

    # Collect ontology-level metadata to carry into every subset.
    # versionInfo, versionIRI, and void:subset are subset-specific and handled below.
    SUBSET_OVERRIDE_PREDICATES = {OWL.versionInfo, OWL.versionIRI, VOID.subset}
    ontology_metadata = [
        (p, o)
        for p, o in g.predicate_objects(SIO_ONT)
        if p not in SUBSET_OVERRIDE_PREDICATES
    ]

    # Write subset files
    ODIR.mkdir(parents=True, exist_ok=True)
    for subset_name, sg in subset_graphs.items():
        subset_file = f"sio-subset-{subset_name}.owl"
        versioned_uri = f"http://semanticscience.org/ontology/sio/v{sio_version}/{subset_file}"
        subset_url = f"http://semanticscience.org/ontology/{subset_file}"

        for p, o in ontology_metadata:
            sg.add((SIO_ONT, p, o))
        sg.add((SIO_ONT, OWL.versionInfo, Literal(subset_file)))
        sg.add((SIO_ONT, OWL.versionIRI, URIRef(versioned_uri)))

        for s in set(sg.subjects()):
            if isinstance(s, URIRef) and "semanticscience" in str(s):
                sg.add((s, RDFS.isDefinedBy, URIRef(versioned_uri)))

        g.add((SIO_ONT, VOID.subset, URIRef(subset_url)))

        print(f"generating {subset_name}")
        sg.serialize(str(ODIR / subset_file), format="xml")

    # Write versioned release file
    print("generating versioned SIO")
    for s in set(g.subjects()):
        if isinstance(s, URIRef) and "semanticscience" in str(s):
            g.add((s, RDFS.isDefinedBy, URIRef("http://semanticscience.org/ontology/sio.owl")))

    g.add((SIO_ONT, OWL.versionIRI, URIRef(version_iri)))
    g.add((SIO_ONT, DCTERMS.modified, Literal(date.today().isoformat(), datatype=XSD.date)))

    shutil.copy(ODIR / "sio-subset-dash-labels.owl", ODIR / "sio-subset-labels.owl")
    g.serialize(str(ODIR / "sio-release.owl"), format="xml")


if __name__ == "__main__":
    main()
