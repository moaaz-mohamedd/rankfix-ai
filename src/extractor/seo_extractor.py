from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any
import json
from urllib.parse import urlparse
from src.utils.text_cleaner import decode_url
from src.utils.validators import extract_domain, normalize_domain

def get_text_or_none(element) -> Optional[str]:
    """
    Return clean text from a BeautifulSoup element.
    If element does not exist, return None.
    """

    if not element:
        return None

    text = element.get_text(strip=True)

    return text if text else None


def get_meta_content(soup: BeautifulSoup, name: str) -> Optional[str]:
    """
    Extract content from meta tag by name.

    Example:
    <meta name="description" content="Page description">
    """

    tag = soup.find("meta", attrs={"name": name})

    if not tag:
        return None

    content = tag.get("content")

    return content.strip() if content else None


def get_canonical(soup: BeautifulSoup) -> Optional[str]:
    """
    Extract canonical URL from:
    <link rel="canonical" href="...">
    """

    tag = soup.find("link", rel="canonical")

    if not tag:
        return None

    href = tag.get("href")

    return href.strip() if href else None


def get_h_tags(soup: BeautifulSoup, tag_name: str) -> List[str]:
    """
    Extract heading tags like h1, h2, h3.
    """

    headings = []

    for tag in soup.find_all(tag_name):
        text = tag.get_text(strip=True)
        if text:
            headings.append(text)

    return headings


def count_words(soup: BeautifulSoup) -> int:
    """
    Count words from visible page text.
    This is a simple version for MVP.
    """

    for script_or_style in soup(["script", "style", "noscript"]):
        script_or_style.extract() ## remove these tags from the soup to avoid counting their content
## VERY IMPORTANT: this function adjust the same soup object
## Which means that in future if u wanna extract any smth from script or style tags u have first to adjust this point.
## it also count the menu and foter words not only the main content, but for MVP it's ok.

    text = soup.get_text(separator=" ", strip=True)
    words = text.split()

    return len(words)


def analyze_images_alt(soup: BeautifulSoup) -> Dict[str, int]:
    """
    Count total images and images missing alt text.
    """

    images = soup.find_all("img")

    total_images = len(images)
    missing_alt = 0

    for image in images:
        alt = image.get("alt")

        if alt is None or not alt.strip():
            missing_alt += 1

    return {
        "total_images": total_images,
        "images_missing_alt": missing_alt
    }

def get_links_data(
    soup: BeautifulSoup,
    page_url: str
) -> Dict[str, int]:
    """
    Analyze internal and external links.
    """

    links = soup.find_all("a")

    total_links = 0
    internal_links = 0
    external_links = 0

    page_domain = extract_domain(page_url)

    for link in links:

        href = link.get("href")

        if not href:
            continue

        # Ignore non SEO links
        if href.startswith(
            (
                "#",
                "mailto:",
                "tel:",
                "javascript:"
            )
        ):
            continue

        total_links += 1


        # Relative URL
        if href.startswith("/"):
            internal_links += 1
            continue


        # Absolute URL
        if href.startswith(
            (
                "http://",
                "https://"
            )
        ):

            link_domain = extract_domain(
                href
            )

            if link_domain == page_domain:
                internal_links += 1

            else:
                external_links += 1


    return {
        "total_links": total_links,
        "internal_links": internal_links,
        "external_links": external_links
    }
    
def get_schema_data(
    soup: BeautifulSoup
) -> Dict[str, Any]:
    """
    Extract JSON-LD schema types.
    """

    schemas = soup.find_all(
        "script",
        attrs={
            "type": "application/ld+json"
        }
    )

    schema_types = []

    for schema in schemas:

        try:
            data = json.loads(
                schema.string
            )

            if isinstance(data, dict):

                schema_type = data.get(
                    "@type"
                )

                if schema_type:
                    schema_types.append(
                        schema_type
                    )

            elif isinstance(data, list):

                for item in data:
                    schema_type = item.get(
                        "@type"
                    )

                    if schema_type:
                        schema_types.append(
                            schema_type
                        )

        except Exception:
            continue


    return {
        "has_schema": len(schema_types) > 0,
        "schema_types": schema_types
    }
    
def get_social_tags(
    soup: BeautifulSoup
) -> Dict[str, Optional[str]]:
    """
    Extract Open Graph and Twitter tags.
    """

    return {

        "og_title": get_meta_property(
            soup,
            "og:title"
        ),

        "og_description": get_meta_property(
            soup,
            "og:description"
        ),

        "og_image": get_meta_property(
            soup,
            "og:image"
        ),

        "twitter_card": get_meta_name(
            soup,
            "twitter:card"
        )

    }
def get_meta_property(
    soup: BeautifulSoup,
    property_name: str
) -> Optional[str]:

    tag = soup.find(
        "meta",
        attrs={
            "property": property_name
        }
    )

    return (
        tag.get("content").strip()
        if tag and tag.get("content")
        else None
    )    

def get_meta_name(
    soup: BeautifulSoup,
    name: str
) -> Optional[str]:

    tag = soup.find(
        "meta",
        attrs={
            "name": name
        }
    )

    return (
        tag.get("content").strip()
        if tag and tag.get("content")
        else None
    )
    
def get_language(
    soup: BeautifulSoup
) -> Optional[str]:
    """
    Extract html language attribute.
    """

    html_tag = soup.find(
        "html"
    )

    if not html_tag:
        return None

    return html_tag.get(
        "lang"
    )
    
def get_text_metrics(
    soup: BeautifulSoup
) -> Dict[str, int]:

    paragraphs = soup.find_all(
        "p"
    )

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return {

        "text_length": len(text),

        "paragraph_count": len(
            paragraphs
        )

    }
    
    
def extract_seo_data(url: str, html: str) -> Dict:
    """
    Extract important SEO elements from page HTML.
    """

    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.find("title")
    title = get_text_or_none(title_tag)

    meta_description = get_meta_content(soup, "description")
    robots_meta = get_meta_content(soup, "robots")

    h1_tags = get_h_tags(soup, "h1")
    h2_tags = get_h_tags(soup, "h2")

    canonical = get_canonical(soup)
    image_data = analyze_images_alt(soup)
    word_count = count_words(soup)
    links_data = get_links_data(
    soup,
    url
)

    schema_data = get_schema_data(
        soup
    )

    social_data = get_social_tags(
        soup
    )

    language = get_language(
        soup
    )

    text_metrics = get_text_metrics(
        soup
    )

    return {
    "url": url,
    "decoded_url": decode_url(url),
    "title": title,
    "title_length": len(title) if title else 0,
    "meta_description": meta_description,
    "meta_description_length": len(meta_description) if meta_description else 0,
    "h1_count": len(h1_tags),
    "h1": h1_tags[0] if h1_tags else None,
    "h2_count": len(h2_tags),
    "canonical": canonical,
    "decoded_canonical": decode_url(canonical) if canonical else None,
    "robots_meta": robots_meta,
    "word_count": word_count,
    "total_images": image_data["total_images"],
    "images_missing_alt": image_data["images_missing_alt"],
    "links": links_data,

    "has_schema": schema_data[
        "has_schema"
    ],

    "schema_types": schema_data[
        "schema_types"
    ],

    "og_title": social_data[
        "og_title"
    ],

    "og_description": social_data[
        "og_description"
    ],

    "og_image": social_data[
        "og_image"
    ],

    "twitter_card": social_data[
        "twitter_card"
    ],

    "language": language,

    "text_length": text_metrics[
        "text_length"
    ],

    "paragraph_count": text_metrics[
        "paragraph_count"
    ],
}