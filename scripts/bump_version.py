#!/usr/bin/env python3
"""Increment the owl:versionInfo version number in sio.owl."""

import argparse
import sys
from datetime import date
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, OWL, XSD

ROOT = Path(__file__).parent.parent
SIO_OWL = ROOT / "ontology" / "sio.owl"
SIO_ONT = URIRef("http://semanticscience.org/ontology/sio.owl")


def parse_version(version_str: str) -> tuple[int, ...]:
    parts = str(version_str).split(".")
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        sys.exit(f"Error: cannot parse version '{version_str}'")


def bump(parts: tuple[int, ...], part: str) -> tuple[int, ...]:
    parts = list(parts)
    # Pad to at least 3 components for patch support
    while len(parts) < 3:
        parts.append(0)
    if part == "major":
        parts[0] += 1
        parts[1] = 0
        parts[2] = 0
    elif part == "minor":
        parts[1] += 1
        parts[2] = 0
    elif part == "patch":
        parts[2] += 1
    # Drop trailing zeros beyond the original width (keep at least major.minor)
    while len(parts) > 2 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def format_version(parts: tuple[int, ...]) -> str:
    return ".".join(str(p) for p in parts)


def main():
    parser = argparse.ArgumentParser(
        description="Bump the owl:versionInfo in ontology/sio.owl."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--major", dest="part", action="store_const", const="major",
                       help="Increment the major version")
    group.add_argument("--minor", dest="part", action="store_const", const="minor",
                       help="Increment the minor version (default)")
    group.add_argument("--patch", dest="part", action="store_const", const="patch",
                       help="Increment the patch version")
    group.add_argument("--set", dest="set_version", metavar="VERSION",
                       help="Set an explicit version string (e.g. 2.0.0)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print the new version without modifying the file")
    parser.add_argument("--file", default=str(SIO_OWL), metavar="PATH",
                        help=f"OWL file to update (default: {SIO_OWL})")
    parser.set_defaults(part="minor")
    args = parser.parse_args()

    owl_path = Path(args.file)
    if not owl_path.exists():
        sys.exit(f"Error: file not found: {owl_path}")

    g = Graph()
    g.parse(str(owl_path))

    old_version_lit = g.value(SIO_ONT, OWL.versionInfo)
    if old_version_lit is None:
        sys.exit(f"Error: no owl:versionInfo found for <{SIO_ONT}>")

    old_str = str(old_version_lit)

    if args.set_version:
        # Validate the explicit version
        parse_version(args.set_version)
        new_str = args.set_version
    else:
        parts = parse_version(old_str)
        new_str = format_version(bump(parts, args.part))

    today = date.today().isoformat()
    print(f"version:  {old_str} -> {new_str}")
    print(f"modified: {today}")

    if args.dry_run:
        return

    # Preserve original Literal attributes (datatype / language tag)
    kwargs = {}
    if old_version_lit.datatype:
        kwargs["datatype"] = old_version_lit.datatype
    if old_version_lit.language:
        kwargs["lang"] = old_version_lit.language

    g.remove((SIO_ONT, OWL.versionInfo, old_version_lit))
    g.add((SIO_ONT, OWL.versionInfo, Literal(new_str, **kwargs)))

    for old_date in list(g.objects(SIO_ONT, DCTERMS.modified)):
        g.remove((SIO_ONT, DCTERMS.modified, old_date))
    g.add((SIO_ONT, DCTERMS.modified, Literal(today, datatype=XSD.date)))

    g.serialize(str(owl_path), format="xml")
    print(f"Updated {owl_path}")


if __name__ == "__main__":
    main()
