from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from src.utils.text_cleaner import decode_url


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
    "images_missing_alt": image_data["images_missing_alt"]
}