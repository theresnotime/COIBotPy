import linkwatcher
import unfurl_archives
import unittest


class TestUnfurls(unittest.TestCase):
    def test_ia_url_is_archive(self):
        self.assertEqual(
            unfurl_archives.is_archive(
                "https://web.archive.org/web/20190521131102/http://www.example.org/"
            ),
            True,
            "URL incorrectly identified as not an archive URL",
        )

    def test_ia_url_unfurl(self):
        self.assertEqual(
            unfurl_archives.unfurl(
                "https://web.archive.org/web/20190521131102/http://www.example.org/"
            ),
            "http://www.example.org/",
            "URL did not unfurl correctly",
        )
        self.assertEqual(
            unfurl_archives.unfurl(
                "https://web.archive.org/web/1234567890/http://www.example.org/nyaa"
            ),
            "http://www.example.org/nyaa",
            "URL did not unfurl correctly",
        )


class TestCOIBot(unittest.TestCase):
    def test_wmf_domains(self):
        self.assertEqual(
            linkwatcher.check_url_allowlists("https://www.wikidata.org/wiki/Q1"),
            True,
            "URL incorrectly identified as not in allowlist",
        )
        self.assertEqual(
            linkwatcher.check_url_allowlists("https://www.example.org"),
            False,
            "URL incorrectly identified as in allowlist",
        )

    def test_url_denylist(self):
        self.assertEqual(
            linkwatcher.check_url_denylists(
                "https://web.archive.org/web/1234567890/http://www.example.org/nyaa"
            ),
            True,
            "URL incorrectly identified as not in denylist",
        )
        self.assertEqual(
            linkwatcher.check_url_denylists("https://www.example.org"),
            False,
            "URL incorrectly identified as in denylist",
        )

    def test_ug_allowlists(self):
        self.assertEqual(
            linkwatcher.check_ug_allowlists({"user_groups": "sysop"}),
            True,
            "User group incorrectly identified as not in allowlist",
        )
        self.assertEqual(
            linkwatcher.check_ug_allowlists({"user_groups": "confirmed"}),
            False,
            "User group incorrectly identified as in allowlist",
        )

    def test_user_denylists(self):
        self.assertEqual(
            linkwatcher.check_user_denylists("JarBot"),
            True,
            "User incorrectly identified as not in denylist",
        )

    def test_project_denylists(self):
        self.assertEqual(
            linkwatcher.check_project_denylists("en.wikipedia.org"),
            False,
            "URL incorrectly identified as in denylist",
        )
        self.assertEqual(
            linkwatcher.check_project_denylists("test.wikipedia.org"),
            True,
            "URL incorrectly identified as not in denylist",
        )

    def test_normalise_url(self):
        self.assertEqual(
            linkwatcher.normalise_url("///www.example.org/test"),
            "//www.example.org/test",
            "URL not normalised correctly",
        )
        self.assertEqual(
            linkwatcher.normalise_url("http://https://example.org"),
            "https://example.org",
            "URL not normalised correctly",
        )
        self.assertEqual(
            linkwatcher.normalise_url("https://doi:%2B10.1007/s00606-018-1514-3"),
            "https://doi.org/10.1007/s00606-018-1514-3",
            "URL not normalised correctly",
        )

    def test_get_project_family(self):
        self.assertEqual(
            linkwatcher.get_project_family("en.wikipedia.org"),
            "wikipedia",
            "Project family not extracted correctly",
        )
        self.assertEqual(
            linkwatcher.get_project_family("commons.wikimedia.org"),
            "commons",
            "Project family not extracted correctly",
        )

    def test_get_registered_domain(self):
        self.assertEqual(
            linkwatcher.get_base_domain("https://www.example.org"),
            "example.org",
            "Registered domain not extracted correctly",
        )
        self.assertEqual(
            linkwatcher.get_base_domain("https://en.wikipedia.org"),
            "wikipedia.org",
            "Registered domain not extracted correctly",
        )


if __name__ == "__main__":
    unittest.main()
