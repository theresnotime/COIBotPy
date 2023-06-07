import COIBot
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
            COIBot.check_url_allowlists("https://www.wikidata.org/wiki/Q1"),
            True,
            "URL incorrectly identified as not in allowlist",
        )
        self.assertEqual(
            COIBot.check_url_allowlists("https://www.example.org"),
            False,
            "URL incorrectly identified as in allowlist",
        )

    def test_ug_allowlists(self):
        self.assertEqual(
            COIBot.check_ug_allowlists({"user_groups": "sysop"}),
            True,
            "User group incorrectly identified as not in allowlist",
        )
        self.assertEqual(
            COIBot.check_ug_allowlists({"user_groups": "confirmed"}),
            False,
            "User group incorrectly identified as in allowlist",
        )

    def test_project_denylists(self):
        self.assertEqual(
            COIBot.check_project_denylists("en.wikipedia.org"),
            False,
            "URL incorrectly identified as in denylist",
        )
        self.assertEqual(
            COIBot.check_project_denylists("test.wikipedia.org"),
            True,
            "URL incorrectly identified as not in denylist",
        )

    def test_normalise_url(self):
        self.assertEqual(
            COIBot.normalise_url("///www.example.org/test"),
            "//www.example.org/test",
            "URL not normalised correctly",
        )

    def test_get_project_family(self):
        self.assertEqual(
            COIBot.get_project_family("en.wikipedia.org"),
            "wikipedia",
            "Project family not extracted correctly",
        )
        self.assertEqual(
            COIBot.get_project_family("commons.wikimedia.org"),
            "commons",
            "Project family not extracted correctly",
        )

    def test_get_registered_domain(self):
        self.assertEqual(
            COIBot.get_registered_domain("https://www.example.org"),
            "example.org",
            "Registered domain not extracted correctly",
        )
        self.assertEqual(
            COIBot.get_registered_domain("https://en.wikipedia.org"),
            "wikipedia.org",
            "Registered domain not extracted correctly",
        )


if __name__ == "__main__":
    unittest.main()
