import requests
from bs4 import BeautifulSoup
from typing import List, Optional
from urllib.parse import urljoin


COMMON_SITEMAP_PATHS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/wp-sitemap.xml",
]


def fetch_url(url: str, timeout: int = 10) -> Optional[str]:
    """
    Fetch URL content and return text if request is successful.
    """

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "RankFixAI-Bot/1.0"
            }
        )

        if response.status_code == 200:
            return response.text

        return None

    except requests.RequestException:
        return None


def find_sitemap(domain: str) -> Optional[str]:
    """
    Try common sitemap locations and return the first working sitemap URL.
    """

    for path in COMMON_SITEMAP_PATHS:
        sitemap_url = urljoin(domain, path)
        content = fetch_url(sitemap_url)

        if content:
            return sitemap_url

    return None


def parse_sitemap_xml(xml_content: str) -> List[str]:
    """
    Parse sitemap XML content and extract all <loc> values.
    """

    soup = BeautifulSoup(xml_content, "xml")

    urls = []

    for loc in soup.find_all("loc"):
        if loc.text:
            urls.append(loc.text.strip())

    return urls


def is_sitemap_index(xml_content: str) -> bool:
    """
    Check if the sitemap is a sitemap index.
    
    Sitemap index means it contains links to other sitemaps,
    not directly to website pages.
    """

    soup = BeautifulSoup(xml_content, "xml")
    return soup.find("sitemapindex") is not None


def get_urls_from_sitemap(domain: str, max_urls: int = 50) -> List[str]:
    """
    Main function:
    1. Find sitemap
    2. Fetch sitemap
    3. Extract URLs
    4. If sitemap index, fetch child sitemaps
    """

    sitemap_url = find_sitemap(domain)

    if not sitemap_url:
        return []

    sitemap_content = fetch_url(sitemap_url)

    if not sitemap_content:
        return []

    extracted_links = parse_sitemap_xml(sitemap_content)

    final_urls = []

    if is_sitemap_index(sitemap_content):
        for child_sitemap_url in extracted_links:
            child_content = fetch_url(child_sitemap_url)

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