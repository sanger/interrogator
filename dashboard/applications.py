import requests
import urllib3
from lxml import etree
from lxml.cssselect import CSSSelector


def fetch_version(url: str, selector: str) -> tuple[str, str]:
    """
    Fetch the version of an application from a webpage using the release link.

    Args:
        url (str): URL of the webpage to fetch the version from.
        selector (str): CSS selector to find the version element.

    Returns:
        tuple[str, str]: Version and release link
    """
    # Disable insecure SSL warnings
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Load webpage
    response = requests.get(url, verify=False)

    # Parse HTML for link in provided selector
    css_selector = CSSSelector(selector + " a")

    # Parse HTML
    parser = etree.HTMLParser()
    html_root = etree.fromstring(response.text, parser)
    links = css_selector(html_root)

    # Return results
    if links:
        return links[0].text, links[0].attrib["href"]
    else:
        return None, None


if __name__ == "__main__":
    lb_version = fetch_version(
        "https://uat.limber.psd.sanger.ac.uk/", ".version-info .container"
    )
    ss_version = fetch_version(
        "https://uat.sequencescape.psd.sanger.ac.uk/", ".deployment-info"
    )

    print(f"Limber version: {lb_version[0]} ({lb_version[1]})")
    print(f"Sequencescape version: {ss_version[0]} ({ss_version[1]})")
