from urllib.parse import unquote


def decode_url(url: str) -> str:
    """
    Decode percent-encoded URLs for better display.

    Example:
    %D8%A7%D8%B3%D8%B9%D8%A7%D8%B1 -> اسعار
    """

    if not url:
        return ""

    return unquote(url)