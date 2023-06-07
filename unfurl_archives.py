import re
import tldextract

known_archive_domains = ["archive.org"]

internet_archive = re.compile(
    r"web\.archive\.org/.*?/(?P<archived_url>https?.*)", re.IGNORECASE
)


def is_archive(url):
    """Check if a URL is an archive URL"""
    if tldextract.extract(url).registered_domain in known_archive_domains:
        return True


def unfurl(url):
    """Unfurl an archive URL"""
    matches = internet_archive.search(url)
    if matches:
        return matches.group("archived_url")
    return False
