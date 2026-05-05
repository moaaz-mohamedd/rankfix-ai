from urllib.parse import urlparse
## urlparse -> is a libirary that breaks down a URL into its components (scheme, netloc, path, etc.) for easier manipulation and validation.
## eg: urlparse("https://example.com/path") -> ParseResult(scheme='https', netloc='example.com', path='/path', params='', query='', fragment='')


#ُ# the def normalize domain syntax just to make it esay to understand that the domain is string and it returns a string as well, and it also helps with type checking and code readability.
## also called Type Hints
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

    if not domain.startswith(("http://", "https://")): ## make sure that damain start with http or https 
                                                       ## bc requests has to include the protocol to work properly
        domain = "https://" + domain

    parsed = urlparse(domain)

    if not parsed.netloc:
        raise ValueError("Invalid domain format.")

    normalized = f"{parsed.scheme}://{parsed.netloc}"

    return normalized.rstrip("/") ## if the domain ends with a slash, remove it to maintain consistency (e.g., https://example.com/ -> https://example.com)