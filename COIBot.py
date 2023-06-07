import allowlists
import config
import denylists
import socket
import sqlite3
import time
import tldextract
from eventstreams import EventStreams
from termcolor import cprint
from unfurl_archives import is_archive, unfurl

CON = sqlite3.connect("coibot.db")


def setup_db():
    cur = CON.cursor()
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS links(
        added_date datetime,
        project_domain text,
        project_family text,
        page_id integer,
        rev_id integer,
        user_text text,
        link_url text,
        base_domain text
    )"""
    )
    CON.commit()


def log_to_db():
    pass


def get_domain_ip(base_domain):
    return socket.gethostbyname(base_domain)


def normalise_url(url):
    """Normalise a URL"""
    # TODO: Add more normalisation, and do this better-er
    url = url.replace("///", "//")
    url = url.replace("http://https://", "https://")  # Happens quite a bit
    url = url.replace("https://https://", "https://")  # Also happens quite a bit
    url = url.replace("doi:%2B", "doi.org/")  # ??
    return url


def get_project_family(project_domain):
    """Get the project family from the project domain"""
    # Odd one out
    if project_domain == "commons.wikimedia.org":
        return "commons"
    return tldextract.extract(project_domain).domain


def get_base_domain(url):
    """Get the base domain from a URL"""
    return tldextract.extract(url).registered_domain


def check_url_allowlists(url):
    """Check if a URL is in the allowlists"""
    registered_domain = get_base_domain(url)
    if registered_domain in allowlists.combined:
        return True
    return False


def check_url_denylists(url):
    """Check if a URL is in the denylists"""
    registered_domain = get_base_domain(url)
    if registered_domain in denylists.domains:
        return True
    return False


def check_project_denylists(project_domain):
    """Check if a project is in the denylists"""
    if project_domain in denylists.projects:
        return True
    return False


def check_ug_allowlists(performer):
    """Check if a user group is in the allowlists"""
    if (
        "user_groups" in performer
        and performer["user_groups"] in allowlists.user_groups
    ):
        return True
    return False


def log(file, message):
    with open(f"{file}.log", "a") as f:
        f.write(f"{message}\n")


if __name__ == "__main__":
    setup_db()
    stream = EventStreams(streams=["page-links-change"], timeout=1)
    # stream.register_filter(external = True)

    print(
        "[added_date] [project_domain] [project_family] [page_id] [rev_id] [user_text] [link_url] [base_domain] [domain_ip]"
    )
    while stream:
        try:
            change = next(iter(stream))

            if change["page_namespace"] not in config.MONITOR_NS:
                cprint(
                    f"Edit to unmonitored namespace ({change['page_namespace']}), skipping",
                    "blue",
                )
                continue

            database = change["database"]
            project_domain = change["meta"]["domain"]

            if check_project_denylists(project_domain):
                cprint(
                    f"Edit to excluded project ({project_domain}), skipping",
                    "blue",
                )
                continue

            performer = change["performer"]
            added_date = change["meta"]["dt"]
            project_family = get_project_family(project_domain)

            # Skip bot edits
            if "user_is_bot" in performer and performer["user_is_bot"]:
                cprint(
                    f"Bot edit by {performer['user_text']} to {project_domain}, skipping",
                    "blue",
                )
                continue

            # Skip edits which don't add links
            if "added_links" in change:
                page_id = change["page_id"]
                page_title = change["page_title"]
                rev_id = change["rev_id"]
                if "user_id" in performer:
                    user_id = performer["user_id"]
                else:
                    user_id = None
                    user_is_ip = True
                user_text = performer["user_text"]

                added_links = change["added_links"]
                for link in added_links:
                    # Skip external links
                    if link["external"]:
                        link_url = normalise_url(link["link"])
                        if check_url_denylists(link_url):
                            cprint("URL in denylist, skipping", "yellow")
                            continue
                        if is_archive(link_url):
                            unfurled = unfurl(link_url)
                            if unfurled is False or unfurled is None or unfurled == "":
                                raise Exception(f"Unfurling {link_url} failed")
                            cprint(f"Unfurling {link_url} to {unfurled}", "yellow")
                            link_url = unfurled
                        if check_url_allowlists(link_url):
                            cprint("URL in allowlist, skipping", "green")
                        elif check_ug_allowlists(performer):
                            cprint("User group in allowlist, skipping", "green")
                        else:
                            base_domain = get_base_domain(link_url)
                            if base_domain is False or base_domain == "":
                                raise Exception(
                                    f"Failed to get base_domain of {link_url}"
                                )
                            domain_ip = get_domain_ip(base_domain)
                            # Print columns for database imput
                            print(
                                f"[{added_date}] [{project_domain}] [{project_family}] [{page_id}] [{rev_id}] [{user_text}] [{link_url}] [{base_domain}] [{domain_ip}]"
                            )
            time.sleep(0.2)
        except KeyError:
            cprint("Caught KeyError exception, skipping", "red")
            continue
        except Exception as e:
            cprint(f"Caught exception: {e}, skipping", "red")
            log("exceptions", str(e))
            continue
