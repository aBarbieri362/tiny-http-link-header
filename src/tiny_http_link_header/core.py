from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from urllib.parse import unquote


@dataclass
class Link:
    """A single parsed link from an HTTP Link header.

    Attributes:
        target: The link target URI (quoted value of the <...> segment).
        params: All link-param key/value pairs, preserving order and allowing
            duplicate keys. ``rel`` is populated here verbatim (space-separated
            tokens), so callers can inspect the raw header if needed.
        rel: The first ``rel`` value, for the common single-relation case. May be None.
    """

    target: str
    params: Dict[str, str] = field(default_factory=dict)
    rel: Optional[str] = None


def _split_top_level(s: str, delimiter: str) -> List[str]:
    """Split a string on the given delimiter, respecting quotes.

    A delimiter inside a quoted parameter value (e.g. title=\"a, b\") must not
    split an entry. We track quote state as we scan.
    """
    entries: List[str] = []
    current: List[str] = []
    in_quotes = False

    for ch in s:
        if ch == '"' and not in_quotes:
            in_quotes = True
            current.append(ch)
        elif ch == '"' and in_quotes:
            in_quotes = False
            current.append(ch)
        elif ch == delimiter and not in_quotes:
            entries.append("".join(current))
            current = []
        else:
            current.append(ch)

    last = "".join(current)
    if last.strip():
        entries.append(last)
    return entries


def _parse_entry(entry: str) -> Optional[Link]:
    """Parse a single `<uri>; param=val; ...` entry.

    Returns None for whitespace-only entries (e.g. trailing comma).
    """
    entry = entry.strip()
    if not entry:
        return None

    # The target URI is enclosed in angle brackets.
    if not entry.startswith("<"):
        return None
    close = entry.find(">")
    if close == -1:
        return None

    target = entry[1:close]
    remainder = entry[close + 1 :]

    params: Dict[str, str] = {}
    rel: Optional[str] = None

    for pair in _split_top_level(remainder, ";"):
        pair = pair.strip()
        if not pair:
            continue
        eq = pair.find("=")
        if eq == -1:
            # RFC 8288 allows bare flag params; we store them as "".
            key = pair.strip()
            if not key:
                continue
            value = ""
        else:
            key = pair[:eq].strip()
            value = pair[eq + 1 :].strip()
            if len(value) >= 2 and value[0] == '"' and value[-1] == '"':
                value = value[1:-1]
                value = unquote(value)
            else:
                value = unquote(value)
        if not key:
            continue
        params[key] = value
        if key == "rel" and rel is None:
            rel = value

    return Link(target=target, params=params, rel=rel)


def parse_link_header(header: str) -> List[Link]:
    """Parse an HTTP Link header value per RFC 8288.

    Returns a list of :class:`Link` objects, one per ``<uri>; ...`` entry.
    Malformed entries are skipped rather than raising; HTTP headers in the wild
    contain stray whitespace and unexpected characters, and a parser that
    aborts on the first oddity leaves the caller with nothing.
    """
    if not header:
        return []

    links: List[Link] = []
    for entry in _split_top_level(header, ","):
        parsed = _parse_entry(entry)
        if parsed is not None:
            links.append(parsed)
    return links
