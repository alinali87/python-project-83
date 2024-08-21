import requests
from bs4 import BeautifulSoup
from requests import Response


def send_request(url: str) -> Response:
    return requests.get(url)


def parse_response(response: Response) -> dict:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Get the title tag value
    title = soup.title.string if soup.title else ''

    # Get the first h1 tag value
    h1 = soup.find('h1').string if soup.find('h1') else ''

    # Print the extracted information
    print(f"Status Code: {response.status_code}")
    print(f"Title: {title}")
    print(f"First h1 Tag: {h1}")
    return {
        "status_code": response.status_code,
        "title": title,
        "h1": h1,
        "description": "",   # TODO: what must be in description?
    }
