import allowlists
import config
import denylists
import mysql.connector
import socket
import time
import tldextract
from datetime import datetime
from eventstreams import EventStreams
from termcolor import cprint
from unfurl_archives import is_archive, unfurl

if config.USE_DB:
    db = mysql.connector.connect(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_DATABASE,
        port=config.DB_PORT,
    )
    cursor = db.cursor()


def log_to_db(
    added_date: str,
    project_domain: str,
    project_family: str,
    page_id: int,
    rev_id: int,
    user_text: str,
    link_url: str,
    base_domain: str,
    domain_ip: str,
    table: str = "global_links",
) -> None:
    sql = f"INSERT INTO {table} (added_date, project_domain, project_family, page_id, rev_id, user_text, link_url, base_domain, domain_ip) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (
        added_date,
        project_domain,
        project_family,
        page_id,
        rev_id,
        user_text,
        link_url,
        base_domain,
        domain_ip,
    )
    cursor.execute(sql, values)
    db.commit()


def get_domain_ip(base_domain):
    """Get the IP address of a domain"""
    return socket.gethostbyname(base_domain)


def normalise_url(url):
    """Normalise a URL"""
    # TODO: Add more normalisation, and do this better-er
    url = url.replace("///", "//")
    url = url.replace("http://https://", "https://")  # Happens quite a bit
    url = url.replace("https://https://", "https://")  # Also happens quite a bit
    url = url.replace("http://http://", "http://")  # How.
    url = url.replace("doi:%2B", "doi.org/")  # ??
    return url


def get_project_family(project_domain):
    """Get the project family from the project domain"""
    # Odd one out
    if project_domain == "commons.wikimedia.org":
        return "commons"
    return tldextract.extract(project_domain).domain


def get_fqdn_domain(url):
    """Get the fqdn from a URL"""
    base_domain = tldextract.extract(url).fqdn
    return base_domain.replace("www.", "")


def get_base_domain(url):
    """Get the base domain from a URL"""
    return tldextract.extract(url).registered_domain


def check_url_allowlists(url):
    """Check if a URL is in the allowlists"""
    registered_domain = get_base_domain(url)
    if registered_domain in allowlists.combined:
        return True
    return False


def check_user_denylists(user):
    """Check if a user is in the denylists"""
    if user in allowlists.users:
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
    """Log a message to a file"""
    with open(file, "a") as f:
        f.write(f"{message}\n")


if __name__ == "__main__":
    stream = EventStreams(streams=["page-links-change"], timeout=1)
    # stream.register_filter(external = True)

    print(
        "[added_date] [project_domain] [project_family] [page_id] [rev_id] [user_text] [link_url] [base_domain] [domain_ip]"
    )
    while stream:
        try:
            change = next(iter(stream))
            added_date = change["meta"]["dt"]
            added_date_obj = datetime.strptime(added_date, "%Y-%m-%dT%H:%M:%SZ")
            added_date_fmt = added_date_obj.strftime("%Y-%m-%d %H:%M:%S")

            if change["page_namespace"] not in config.MONITOR_NS:
                cprint(
                    f"[{added_date_fmt}] Edit to unmonitored namespace ({change['page_namespace']}), skipping",
                    "blue",
                )
                continue

            database = change["database"]
            project_domain = change["meta"]["domain"]

            if check_project_denylists(project_domain):
                cprint(
                    f"[{added_date_fmt}] Edit to excluded project ({project_domain}), skipping",
                    "blue",
                )
                continue

            performer = change["performer"]
            project_family = get_project_family(project_domain)

            # Skip bot edits
            if "user_is_bot" in performer and performer["user_is_bot"]:
                cprint(
                    f"[{added_date_fmt}] Bot edit by {performer['user_text']} to {project_domain}, skipping",
                    "blue",
                )
                continue

            # Check performer against denylist
            if check_user_denylists(performer["user_text"]):
                cprint(
                    f"[{added_date_fmt}] User {performer['user_text']} is in denylist, skipping",
                    "yellow",
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
                            cprint(
                                f"[{added_date_fmt}] URL in denylist, skipping",
                                "yellow",
                            )
                            continue
                        if is_archive(link_url):
                            unfurled = unfurl(link_url)
                            if unfurled is False or unfurled is None or unfurled == "":
                                raise Exception(f"Unfurling {link_url} failed")
                            cprint(f"Unfurling {link_url} to {unfurled}", "yellow")
                            link_url = unfurled
                        if check_url_allowlists(link_url):
                            cprint(
                                f"[{added_date_fmt}] URL in allowlist, skipping",
                                "yellow",
                            )
                        elif check_ug_allowlists(performer):
                            cprint(
                                f"[{added_date_fmt}] User group in allowlist, skipping",
                                "yellow",
                            )
                        else:
                            fqdn_domain = get_fqdn_domain(link_url)
                            base_domain = get_base_domain(link_url)
                            if base_domain is False or base_domain == "":
                                raise Exception(
                                    f"Failed to get base_domain of {link_url}"
                                )
                            domain_ip = get_domain_ip(base_domain)
                            # Print columns for database imput

                            log_entry = f"{added_date_fmt},{project_domain},{project_family},{page_id},{rev_id},{user_text},{link_url},{fqdn_domain},{domain_ip}"
                            cprint(log_entry, "green")

                            # Log to database
                            if config.USE_DB:
                                log_to_db(
                                    added_date_fmt,
                                    project_domain,
                                    project_family,
                                    page_id,
                                    rev_id,
                                    user_text,
                                    link_url,
                                    fqdn_domain,
                                    domain_ip,
                                )
            time.sleep(0.1)
        except KeyError:
            cprint("Caught KeyError exception, skipping", "red")
            continue
        except Exception as e:
            cprint(f"Caught exception: {e}, skipping", "red")
            log("exceptions.log", str(e))
            continue