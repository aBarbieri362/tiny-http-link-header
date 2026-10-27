# tiny-http-link-header

Parses HTTP `Link` headers (RFC 8288) into a list of structured `Link` objects with their parameters.

```python
from tiny_http_link_header import parse_link_header, Link

links = parse_link_header(
    '<https://api.example.com/page2>; rel="next"; type="application/json", '
    '<https://api.example.com/page0>; rel="prev"; title="Previous"'
)
for link in links:
    print(link.target, link.rel, link.params)
# https://api.example.com/page2 next {'rel': 'next', 'type': 'application/json'}
# https://api.example.com/page0 prev {'rel': 'prev', 'title': 'Previous'}
```

## Why this exists

Real-world HTTP responses ship `Link` headers with quoted values, commas inside
quotes, bare flag parameters, and percent-encoded characters. This library
handles those without pulling in a dependency. The trade-off: it does not
resolve relative URIs against a base (RFC 3986 §5), because that requires a
base URI the header alone does not provide. If you need resolution, apply it to
`link.target` yourself.

## Edge you will hit

Malformed entries (missing `<`, unclosed `>`, etc.) are skipped silently rather
than raising. If a header is corrupt, `parse_link_header` returns the links it
could parse and drops the rest.

## Exports

- `parse_link_header(header: str) -> list[Link]` — the parser.
- `Link` — dataclass with `target: str`, `params: dict[str, str]`, and
  `rel: str | None` (the first `rel` value for convenience).

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

