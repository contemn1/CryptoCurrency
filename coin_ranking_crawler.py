import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime, timedelta
import re

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


def parse(html_page):
    soup = BeautifulSoup(html_page, 'html.parser')
    res = []
    for news_blocks in soup.find_all("tr", attrs={"class": "text-right"}):
        row = []
        children = news_blocks.findChildren()
        for ele in children:
            row.append(ele.text)
        row[0] = datetime.strptime(row[0], "%b %d, %Y").strftime("%Y-%m-%d")
        row[1:] = [re.sub(",", "", num) for num in row[1:]]
        res.append(row)

    res = res[::-1]
    return res

if __name__ == '__main__':
    url = "https://coinmarketcap.com/currencies/bitcoin-cash/historical-data/?start=20170425&end=20180425"
    page = fetch_url(url)
    result = parse(page)
    print("\t".join(["Date", "Open", "High", "Low", "Close", "Volume", "Market Cap"]))
    for ele in result:
        print("\t".join(ele))