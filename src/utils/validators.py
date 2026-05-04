from urllib.parse import urlparse


def normalize_domain(domain: str) -> str:
    """
    Normalize user input domain.

    Examples:
    example.com              -> https://example.com
    https://example.com/     -> https://example.com
    http://example.com       -> http://example.com
    """

    if not domain:
        raise ValueError("Domain cannot be empty.")

    domain = domain.strip()

    if not domain.startswith(("http://", "https://")):
        domain = "https://" + domain

    parsed = urlparse(domain)

    if not parsed.netloc:
        raise ValueError("Invalid domain format.")

    normalized = f"{parsed.scheme}://{parsed.netloc}"

    return normalized.rstrip("/")