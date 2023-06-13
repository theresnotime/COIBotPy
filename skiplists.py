# Ignore WMF domain additions
wmf_domains = [
    "toolforge.org",
    "wikimedia.org",
    "wikimediafoundation.org",
    "wikibooks.org",
    "wikidata.org",
    "wikinews.org",
    "wikipedia.org",
    "wikiquote.org",
    "wikisource.org",
    "wikiversity.org",
    "wikivoyage.org",
    "wiktionary.org",
    "mediawiki.org",
    "wmflabs.org",
    "wmcloud.org",
]

# Ignore some other common, but non-spam, domains
# TODO: Move this list on-wiki
other_domains = [
    "creativecommons.org",
    "openstreetmap.org",
    "worldcat.org",
]

# Temp: Ignore these archive domains
archive_domains = [
    "archive.org",
    "archive.is",
    "archive.today",
]

# Combine the lists
combined = wmf_domains + other_domains + archive_domains

# Don't run on these projects
projects = [
    "test.wikipedia.org",
    "test2.wikipedia.org",
]

# Ignore these users
# TODO: Move this list on-wiki
users = [
    "JarBot",  # Not marked as a bot
    "LinguisticMystic",  # High rate of link additions, does not require review
]

# Ignore users in these user groups
# TODO: Move this list on-wiki
user_groups = [
    "sysop",
    "bot",
    "steward",
]
