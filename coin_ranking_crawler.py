import requests
from bs4 import BeautifulSoup
import logging

headers = {"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.146 Safari/537.36"}

def fetch_url(url, header_dict=headers, record_error=None):
    try:
        result = requests.get(url, headers=header_dict)
        return result.content

    except requests.ConnectionError as err:
        logging.error("Failed to connect url {0}".format(err))
        if record_error is not None:
            record_error(url)
        return ""
