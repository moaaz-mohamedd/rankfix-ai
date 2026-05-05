from shutil import which

import requests ## library for making HTTP requests to fetch sitemap content from the web 
from bs4 import BeautifulSoup ## library for parsing XML and HTML content, used to extract URLs from the sitemap XML
from typing import List, Optional ## List and Optional are used for type hints to indicate that a function returns a list of strings or an optional string (which can be None)
from urllib.parse import urljoin ## urljoin is used to construct absolute URLs from relative paths, ensuring that we can correctly build sitemap URLs based on the domain provided by the user


COMMON_SITEMAP_PATHS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/wp-sitemap.xml",
]


def fetch_url_content(url: str, timeout: int = 10) -> Optional[str]: ## fetch url of the sitemap and return the content as a string or none
    """
    Fetch URL content and return text if request is successful.
    """

    try:
        response = requests.get(
            url,
            timeout=timeout, ## set a timeout to prevent hanging if the server is slow or unresponsive
            headers={
                "User-Agent": "RankFixAI-Bot/1.0" ## set a custom User-Agent to identify our crawler, which can help with debugging and also ensures that some servers that block unknown agents will allow our requests
            }
        )

        if response.status_code == 200:
            return response.text

        return None

    except requests.RequestException:
        return None


def get_sitemap_url(domain: str) -> Optional[str]: ## function that takes domain and joins it with common sitemap paths to find the sitemap URL, returns the first valid sitemap URL or None if not found
    """
    Try common sitemap locations and return the first working sitemap URL.
    """

    for path in COMMON_SITEMAP_PATHS:
        sitemap_url = urljoin(domain, path)
        content = fetch_url_content(sitemap_url)

        if content:
            return sitemap_url

    return None

def is_sitemap_index(xml_content: str) -> bool:
    """
    Check if the sitemap is a sitemap index.
    
    Sitemap index means it contains links to other sitemaps,
    not directly to website pages.
    """

    soup = BeautifulSoup(xml_content, "xml")     
    return soup.find("sitemapindex") is not None 


def parse_sitemap_xml(xml_content: str) -> List[str]:
    """
    Parse sitemap XML content and extract all <loc> values.
    """

    soup = BeautifulSoup(xml_content, "xml") ## parse the XML content using BeautifulSoup with the "xml" parser, which allows us to easily navigate the XML structure and extract the relevant data (in this case, the URLs contained within <loc> tags)

    urls = []

    for loc in soup.find_all("loc"):
        if loc.text:
            urls.append(loc.text.strip())

    return urls



## Main function:
def get_urls_from_sitemap(domain: str, max_urls: int = 50) -> List[str]:
    """
    Main function:
    1. Find sitemap
    2. Fetch sitemap
    3. Extract URLs
    4. If sitemap index, fetch child sitemaps
    """

    sitemap_url = get_sitemap_url(domain)

    if not sitemap_url:
        return []

    sitemap_content = fetch_url_content(sitemap_url)

    if not sitemap_content:
        return []

    extracted_links = parse_sitemap_xml(sitemap_content) ## extract urls of content whethee they are pages or child sitemaps

    final_urls = []

    if is_sitemap_index(sitemap_content):
        for child_sitemap_url in extracted_links:
            child_content = fetch_url_content(child_sitemap_url)

            if not child_content:
                continue

            page_urls = parse_sitemap_xml(child_content)

            for page_url in page_urls:
                final_urls.append(page_url)

                if len(final_urls) >= max_urls:
                    return final_urls

    else:
        final_urls = extracted_links[:max_urls]

    return final_urls