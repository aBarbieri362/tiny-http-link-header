import unittest
from tiny_http_link_header import parse_link_header, Link


class TestParseLinkHeader(unittest.TestCase):
    def test_single_link_with_rel(self):
        result = parse_link_header('<https://api.example.com/users>; rel="next"')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].target, "https://api.example.com/users")
        self.assertEqual(result[0].rel, "next")
        self.assertEqual(result[0].params["rel"], "next")

    def test_multiple_links(self):
        result = parse_link_header(
            '<https://api.example.com/page1>; rel="prev", '
            '<https://api.example.com/page3>; rel="next"'
        )
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].rel, "prev")
        self.assertEqual(result[1].rel, "next")

    def test_multiple_params(self):
        result = parse_link_header(
            '<https://api.example.com/schema>; rel="describedby"; '
            'type="application/schema+json"; title="Schema"'
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].target, "https://api.example.com/schema")
        self.assertEqual(result[0].rel, "describedby")
        self.assertEqual(result[0].params["type"], "application/schema+json")
        self.assertEqual(result[0].params["title"], "Schema")

    def test_rel_without_quotes(self):
        result = parse_link_header("<https://api.example.com/next>; rel=next")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].rel, "next")

    def test_anchor_param(self):
        result = parse_link_header(
            '<https://api.example.com/profile>; rel="alternate"; anchor="https://api.example.com/me"'
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].params["anchor"], "https://api.example.com/me")

    def test_empty_header(self):
        self.assertEqual(parse_link_header(""), [])

    def test_whitespace_only_header(self):
        self.assertEqual(parse_link_header("   "), [])

    def test_comma_in_quoted_value(self):
        result = parse_link_header(
            '<https://api.example.com/docs>; rel="help"; title="See: docs, and more"'
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].params["title"], "See: docs, and more")

    def test_multiple_rel_tokens(self):
        # The rel extension can list several relation types separated by spaces.
        result = parse_link_header(
            '<https://api.example.com/auth>; rel="http://example.org/rel/auth alternate"'
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(
            result[0].rel, "http://example.org/rel/auth alternate"
        )

    def test_url_percent_decoded_in_quoted_value(self):
        result = parse_link_header(
            '<https://api.example.com/path>; title="hello%20world"'
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].params["title"], "hello world")

    def test_no_params(self):
        result = parse_link_header("<https://api.example.com/bare>")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].target, "https://api.example.com/bare")
        self.assertEqual(result[0].params, {})
        self.assertIsNone(result[0].rel)

    def test_trailing_comma(self):
        result = parse_link_header('<https://api.example.com/a>; rel="next",')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].rel, "next")

    def test_bare_flag_param(self):
        # A param with no '=' is stored with an empty string value.
        result = parse_link_header(
            '<https://api.example.com/x>; rel="next"; crossorigin'
        )
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].params["crossorigin"], "")

    def test_link_is_dataclass(self):
        result = parse_link_header('<https://api.example.com/a>; rel="next"')
        self.assertIsInstance(result[0], Link)


if __name__ == "__main__":
    unittest.main()
