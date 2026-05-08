import requests
from typing import Dict, Optional


def fetch_page(url: str, timeout: int = 10) -> Dict[str, Optional[any]]:
    """
    Fetch a web page and return useful response data.

    This function opens a URL and returns:
    - original URL
    - final URL after redirects
    - status code
    - HTML content
    - error message if request failed
    """

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "RankFixAI-Bot/1.0"
            },
            allow_redirects=True
        )

        return {
            "url": url,
            "final_url": response.url,
            "status_code": response.status_code,
            "html": response.text if response.status_code == 200 else None,
            "error": None
        }

    except requests.RequestException as error:
        return {
            "url": url,
            "final_url": None,
            "status_code": None,
            "html": None,
            "error": str(error)
        }