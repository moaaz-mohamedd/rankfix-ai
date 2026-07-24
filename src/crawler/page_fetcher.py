import requests
from typing import Dict, Optional, Any
import time


def fetch_page(url: str, timeout: int = 10) -> Dict[str, Any]:
    """
    Fetch a web page and return HTTP response data.

    Returns:
    - original URL
    - final URL after redirects
    - status code
    - HTML content
    - response headers
    - response time
    - error message
    """

    start_time = time.time()

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "RankFixAI-Bot/1.0"
            },
            allow_redirects=True
        )

        response_time = round(
            time.time() - start_time,
            3
        )

        return {
            "url": url,
            "final_url": response.url,
            "status_code": response.status_code,
            "html": response.text,
            "headers": dict(response.headers),
            "content_type": response.headers.get(
                "Content-Type"
            ),
            "response_time": response_time,
            "error": None
        }

    except requests.Timeout:
        return {
            "url": url,
            "final_url": None,
            "status_code": None,
            "html": None,
            "headers": None,
            "content_type": None,
            "response_time": None,
            "error": "Request timeout"
        }

    except requests.RequestException as error:
        return {
            "url": url,
            "final_url": None,
            "status_code": None,
            "html": None,
            "headers": None,
            "content_type": None,
            "response_time": None,
            "error": str(error)
        }