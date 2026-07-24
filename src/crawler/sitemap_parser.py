from __future__ import annotations

import gzip
import logging
from collections import deque
from typing import List, Optional, TypedDict
from urllib.parse import urljoin
from xml.etree import ElementTree

import requests


logger = logging.getLogger(__name__)

USER_AGENT = "RankFixAI-Bot/1.0"

COMMON_SITEMAP_PATHS = [
    "/sitemap.xml",
    "/sitemap_index.xml",
    "/wp-sitemap.xml",
]

VALID_SITEMAP_ROOTS = {
    "urlset",
    "sitemapindex",
}

MAX_SITEMAPS_TO_VISIT = 500


class FetchResult(TypedDict):
    """
    Structured result returned after fetching a URL.
    """

    requested_url: str
    final_url: str
    status_code: int
    content: str


def fetch_url_content(
    url: str,
    timeout: int = 10,
) -> Optional[FetchResult]:
    """
    Fetch URL content and preserve redirect information.

    Returns:
        {
            "requested_url": original requested URL,
            "final_url": final URL after redirects,
            "status_code": final response status code,
            "content": decoded response content,
        }

    Returns None only when a network-level error occurs.
    """

    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": (
                    "application/xml,"
                    "text/xml,"
                    "text/plain,"
                    "*/*"
                ),
            },
        )

        status_code = response.status_code
        final_url = response.url

        # Preserve response information even when the HTTP status is not successful.
        if not 200 <= status_code < 300:
            logger.warning(
                "Could not fetch sitemap URL %s. Final URL: %s. Status: %s",
                url,
                final_url,
                status_code,
            )

            return {
                "requested_url": url,
                "final_url": final_url,
                "status_code": status_code,
                "content": "",
            }

        raw_content = response.content

        # GZIP files start with this magic number.
        if raw_content.startswith(b"\x1f\x8b"):
            raw_content = gzip.decompress(raw_content)

        encoding = response.encoding or "utf-8"

        try:
            decoded_content = raw_content.decode(encoding)

        except (LookupError, UnicodeDecodeError):
            decoded_content = raw_content.decode(
                "utf-8",
                errors="replace",
            )

        return {
            "requested_url": url,
            "final_url": final_url,
            "status_code": status_code,
            "content": decoded_content,
        }

    except (requests.RequestException, OSError, EOFError) as error:
        logger.warning(
            "Could not fetch %s: %s",
            url,
            error,
        )

        return None


def _local_tag_name(tag: str) -> str:
    """
    Return an XML tag name without its namespace.

    Example:
        {http://www.sitemaps.org/schemas/sitemap/0.9}urlset

    Becomes:
        urlset
    """

    return tag.rsplit("}", 1)[-1].lower()


def get_sitemap_type(xml_content: str) -> Optional[str]:
    """
    Detect the sitemap XML type.

    Returns:
        "urlset" when the sitemap contains page URLs.

        "sitemapindex" when the sitemap contains child sitemaps.

        None when the content is not valid sitemap XML.
    """

    if not xml_content or not xml_content.strip():
        return None

    try:
        root = ElementTree.fromstring(xml_content)

    except ElementTree.ParseError:
        return None

    root_name = _local_tag_name(root.tag)

    if root_name not in VALID_SITEMAP_ROOTS:
        return None

    return root_name


def is_valid_sitemap_xml(xml_content: str) -> bool:
    """
    Check whether the supplied content is valid sitemap XML.
    """

    return get_sitemap_type(xml_content) is not None


def is_sitemap_index(xml_content: str) -> bool:
    """
    Check whether the sitemap contains child sitemap URLs.
    """

    return get_sitemap_type(xml_content) == "sitemapindex"


def parse_sitemap_xml(xml_content: str) -> List[str]:
    """
    Extract all non-empty <loc> values from sitemap XML.
    """

    if not is_valid_sitemap_xml(xml_content):
        return []

    try:
        root = ElementTree.fromstring(xml_content)

    except ElementTree.ParseError:
        return []

    links: List[str] = []

    for element in root.iter():
        tag_name = _local_tag_name(element.tag)

        if tag_name != "loc":
            continue

        if element.text and element.text.strip():
            links.append(
                element.text.strip()
            )

    return links


def get_sitemaps_from_robots(domain: str) -> List[str]:
    """
    Read all Sitemap directives from robots.txt.

    The sitemap URLs found here receive the highest discovery priority.
    """

    robots_url = urljoin(
        f"{domain.rstrip('/')}/",
        "robots.txt",
    )

    fetch_result = fetch_url_content(
        robots_url
    )

    if not fetch_result:
        return []

    if not 200 <= fetch_result["status_code"] < 300:
        return []

    robots_content = fetch_result["content"]

    if not robots_content:
        return []

    sitemap_urls: List[str] = []

    seen_urls = set()

    for raw_line in robots_content.splitlines():
        # Remove any comment written after #.
        line = raw_line.split("#", 1)[0].strip()

        if not line or ":" not in line:
            continue

        directive, value = line.split(":", 1)

        if directive.strip().lower() != "sitemap":
            continue

        sitemap_value = value.strip()

        if not sitemap_value:
            continue

        sitemap_url = urljoin(
            fetch_result["final_url"],
            sitemap_value,
        )

        if sitemap_url in seen_urls:
            continue

        sitemap_urls.append(
            sitemap_url
        )

        seen_urls.add(
            sitemap_url
        )

    return sitemap_urls


def discover_sitemap_urls(domain: str) -> List[str]:
    """
    Build an ordered list of sitemap candidates.

    Priority:
        1. Sitemap URLs declared inside robots.txt.
        2. Common sitemap paths as fallback candidates.

    Duplicate candidates are removed while preserving their order.
    """

    candidates = get_sitemaps_from_robots(
        domain
    )

    candidates.extend(
        urljoin(
            f"{domain.rstrip('/')}/",
            path.lstrip("/"),
        )
        for path in COMMON_SITEMAP_PATHS
    )

    unique_candidates: List[str] = []

    seen_candidates = set()

    for candidate in candidates:
        candidate = candidate.strip()

        if not candidate:
            continue

        if candidate in seen_candidates:
            continue

        unique_candidates.append(
            candidate
        )

        seen_candidates.add(
            candidate
        )

    return unique_candidates


def get_sitemap_url(domain: str) -> Optional[str]: # this function only get the final url and check for xml of the discoverd candidates 
    # to prevent duplicate crawling
    """
    Return the final URL of the first valid discovered sitemap.

    If the candidate redirects, the URL returned here is the redirect target.
    """

    sitemap_candidates = discover_sitemap_urls(
        domain
    )

    visited_final_urls = set()

    for sitemap_url in sitemap_candidates:
        fetch_result = fetch_url_content(
            sitemap_url
        )

        if not fetch_result:
            continue

        if not 200 <= fetch_result["status_code"] < 300:
            continue

        final_url = fetch_result["final_url"]

        if final_url in visited_final_urls:
            continue

        visited_final_urls.add(
            final_url
        )

        sitemap_content = fetch_result["content"]

        if is_valid_sitemap_xml(sitemap_content):
            return final_url

    return None


def get_urls_from_sitemap(
    domain: str,
    max_urls: int = 50,
) -> List[str]:
    """
    Discover unique page URLs from normal or nested sitemap files.

    Redirect targets are used as the sitemap identity to prevent the same
    sitemap resource from being parsed more than once.
    """

    if max_urls <= 0:
        return []

    sitemap_candidates = discover_sitemap_urls(
        domain
    )

    sitemap_queue = deque(
        sitemap_candidates
    )

    # URLs currently waiting inside the queue.
    queued_sitemaps = set(
        sitemap_candidates
    )

    # Candidate URLs that have already been requested.
    requested_sitemaps = set()

    # Final sitemap URLs that have already been handled.
    visited_sitemaps = set()

    # Map requested aliases to their final redirect targets.
    redirect_targets = {}

    seen_page_urls = set()

    final_urls: List[str] = []

    while (
        sitemap_queue
        and len(final_urls) < max_urls
        and len(requested_sitemaps) < MAX_SITEMAPS_TO_VISIT
    ):
        sitemap_url = sitemap_queue.popleft()

        queued_sitemaps.discard(
            sitemap_url
        )

        # Prevent requesting the exact same candidate twice.
        if sitemap_url in requested_sitemaps:
            continue

        # The candidate itself might be a final URL already handled
        # through another redirecting candidate.
        if sitemap_url in visited_sitemaps:
            continue

        known_final_url = redirect_targets.get(
            sitemap_url
        )

        if (
            known_final_url
            and known_final_url in visited_sitemaps
        ):
            continue

        requested_sitemaps.add(
            sitemap_url
        )

        fetch_result = fetch_url_content(
            sitemap_url
        )

        if not fetch_result:
            continue

        if not 200 <= fetch_result["status_code"] < 300:
            continue

        final_sitemap_url = fetch_result["final_url"]

        # Remember that the requested candidate points to this final URL.
        redirect_targets[sitemap_url] = final_sitemap_url

        # The final resource may have already been parsed through another URL.
        if final_sitemap_url in visited_sitemaps:
            continue

        # Mark the final URL before parsing so aliases cannot parse it again.
        visited_sitemaps.add(
            final_sitemap_url
        )

        sitemap_content = fetch_result["content"]

        if not sitemap_content:
            continue

        sitemap_type = get_sitemap_type(
            sitemap_content
        )

        # Prevent HTML pages or unrelated XML files from being treated
        # as sitemap files.
        if sitemap_type is None:
            continue

        extracted_links = parse_sitemap_xml(
            sitemap_content
        )

        if sitemap_type == "sitemapindex":
            for child_link in extracted_links:
                child_sitemap_url = urljoin(
                    final_sitemap_url,
                    child_link,
                )

                known_child_final_url = redirect_targets.get(
                    child_sitemap_url
                )

                if child_sitemap_url in requested_sitemaps:
                    continue

                if child_sitemap_url in queued_sitemaps:
                    continue

                if child_sitemap_url in visited_sitemaps:
                    continue

                if (
                    known_child_final_url
                    and known_child_final_url in visited_sitemaps
                ):
                    continue

                sitemap_queue.append(
                    child_sitemap_url
                )

                queued_sitemaps.add(
                    child_sitemap_url
                )

            continue

        for page_link in extracted_links:
            page_url = urljoin(
                final_sitemap_url,
                page_link,
            )

            if page_url in seen_page_urls:
                continue

            seen_page_urls.add(
                page_url
            )

            final_urls.append(
                page_url
            )

            if len(final_urls) >= max_urls:
                break

    return final_urls