#!/usr/bin/env python3
"""Validate atlas structure and embedded-data parity; NOT literary accuracy."""
from __future__ import annotations
import argparse
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import sys
from typing import Any


class EmbeddedData(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.active = False
        self.parts: list[str] = []
        self.count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'script' and dict(attrs).get('id') == 'data':
            self.active = True
            self.count += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == 'script':
            self.active = False

    def handle_data(self, data: str) -> None:
        if self.active:
            self.parts.append(data)


def validate(data: Any, html: str | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not isinstance(data, dict):
        return {'errors': ['Dataset must be an object'], 'warnings': warnings, 'counts': {}}
    sources = data.get('sources')
    if not isinstance(sources, dict):
        errors.append('sources must be an object')
        sources = {}
    for key, source in sources.items():
        if not isinstance(source, dict) or source.get('tier') not in ('primary', 'secondary'):
            errors.append(f'sources.{key}: invalid source or tier')
        elif not isinstance(source.get('url'), str) or not source['url'].startswith('https://'):
            errors.append(f'sources.{key}: missing HTTPS source URL')
    collections: dict[str, list[dict[str, Any]]] = {}
    indexes: dict[str, dict[str, dict[str, Any]]] = {}
    for key in ('routes', 'nodes', 'edges', 'events', 'relations'):
        raw = data.get(key)
        if not isinstance(raw, list):
            errors.append(f'{key} must be a list')
            raw = []
        if any(not isinstance(record, dict) for record in raw):
            errors.append(f'{key} contains non-object records')
        records = [record for record in raw if isinstance(record, dict)]
        collections[key] = records
        indexes[key] = {}
        if key == 'relations':
            continue
        for record in records:
            rid = record.get('id')
            if not isinstance(rid, str) or not rid:
                errors.append(f'{key}: missing string ID')
            elif rid in indexes[key]:
                errors.append(f'{key}: duplicate ID {rid}')
            else:
                indexes[key][rid] = record

    def reference(value: Any, table: dict, where: str) -> None:
        if not isinstance(value, str) or value not in table:
            errors.append(f'{where}: unknown reference {value!r}')

    for key, records in collections.items():
        for i, record in enumerate(records):
            where = f'{key}.{record.get("id", i)}'
            refs = record.get('sources')
            if not isinstance(refs, list) or not refs:
                errors.append(f'{where}: missing source references')
            else:
                for source in refs:
                    reference(source, sources, where + '.sources')
            chapter = record.get('chapter')
            if chapter is not None and (type(chapter) is not int or chapter < 1):
                errors.append(f'{where}: chapter must be positive integer or null')

    seen_aliases: set[tuple[str, str]] = set()
    for node in collections['nodes']:
        where = f'nodes.{node.get("id")}'
        if type(node.get('number')) is not int or node['number'] < 0:
            errors.append(f'{where}: invalid station number')
        memberships = node.get('routes', [])
        if not isinstance(memberships, list):
            errors.append(f'{where}: routes must be a list')
            memberships = []
        for route in memberships:
            reference(route, indexes['routes'], where + '.routes')
        coords = [node.get('x'), node.get('y')]
        if any(v is not None for v in coords) and not all(
            type(v) in (int, float) and math.isfinite(v) for v in coords
        ):
            errors.append(f'{where}: coordinates must be a finite pair or both null')
        aliases = node.get('aliases', {})
        if not isinstance(aliases, dict):
            errors.append(f'{where}: aliases must be an object')
            aliases = {}
        for route, alias in aliases.items():
            if route not in memberships or not isinstance(alias, str) or not alias:
                errors.append(f'{where}: invalid alias or alias membership')
                continue
            key = (route, alias)
            if key in seen_aliases:
                errors.append(f'{where}: duplicate service alias {key}')
            seen_aliases.add(key)
        if node.get('tier') == 'primary':
            refs = node.get('sources', [])
            if not isinstance(refs, list) or not any(
                isinstance(s, str) and isinstance(sources.get(s), dict)
                and sources[s].get('tier') == 'primary' for s in refs
            ):
                errors.append(f'{where}: primary label lacks primary source reference')

    for record in collections['edges'] + collections['relations']:
        where = str(record.get('id', 'relation'))
        for endpoint in ('from', 'to'):
            reference(record.get(endpoint), indexes['nodes'], where + '.' + endpoint)
        if 'route' in record:
            reference(record['route'], indexes['routes'], where + '.route')
    for event in collections['events']:
        where = f'events.{event.get("id")}'
        location, travel = event.get('location'), event.get('travel')
        if location is not None:
            reference(location, indexes['nodes'], where + '.location')
        if location is not None and travel is not None:
            errors.append(f'{where}: location and travel cannot both be set')
        if travel is not None:
            if not isinstance(travel, dict):
                errors.append(f'{where}: travel must be an object')
                continue
            reference(travel.get('to'), indexes['nodes'], where + '.travel.to')
            if travel.get('from') is not None:
                reference(travel['from'], indexes['nodes'], where + '.travel.from')
            if travel.get('route') is not None:
                reference(travel['route'], indexes['routes'], where + '.travel.route')

    # Existing published aliases are compatibility contracts, not canonical names.
    stable = {'red-yellow-83': '83(a)', 'tangerine-plum-83': '83(b)',
              'mauve-purple-283': '283(a)', 'green-yellow-283': '283(b)'}
    for rid, alias in stable.items():
        record = indexes['nodes'].get(rid, {})
        aliases = record.get('aliases', {})
        if not isinstance(aliases, dict) or aliases.get('nightmare') != alias:
            errors.append(f'{rid}: published alias changed; explicit migration required')
    if html is not None:
        parser = EmbeddedData()
        parser.feed(html)
        try:
            embedded = json.loads(''.join(parser.parts))
            if parser.count != 1 or embedded != data:
                errors.append('index.html embedded dataset differs from data.json')
        except (ValueError, TypeError):
            errors.append('index.html embedded dataset is missing or invalid')
    counts = {key: len(records) for key, records in collections.items()}
    counts['inferred_sequences'] = sum(e.get('kind') == 'sequence' for e in collections['edges'])
    counts['primary_nodes'] = sum(n.get('tier') == 'primary' for n in collections['nodes'])
    warnings.append('Structural validation does not establish book accuracy or spoiler safety.')
    if counts['inferred_sequences']:
        warnings.append(f'{counts["inferred_sequences"]} inferred sequence edges are not verified directions.')
    if counts['primary_nodes'] < counts['nodes']:
        warnings.append('Primary-text verification remains incomplete.')
    return {'errors': errors, 'warnings': warnings, 'counts': counts}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        result = validate(json.loads((args.root / 'data.json').read_text(encoding='utf-8')),
                          (args.root / 'index.html').read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        print(f'Input error: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
