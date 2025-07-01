import time
from typing import Sized
from fake_useragent import UserAgent

import dateutil.parser
import requests
from bs4 import BeautifulSoup

from requests import Session
from http.cookiejar import DefaultCookiePolicy


def get_author(row):
    author = row.find_all('td', class_="author")[0].div.a.get_text().strip()
    author = author.split(", ")
    author.reverse()
    author = " ".join(author)
    return author


def get_title(row):
    return row.find_all('td', class_="title")[0].div.a.get_text().strip().splitlines()[0]


def get_link(row):
    link = row.find_all('td', class_="title")[0].div.a['href']
    link = "https://www.goodreads.com{}".format(link)
    return link


def get_num_pages(row):
    try:
        return int(row.find_all('td', class_="num_pages")[0].div.nobr.get_text().strip().splitlines()[0])
    except:
        return None


def get_date(row, class_):
    try:
        field = row.find_all('td', class_=class_)[0].div.get_text().strip()
        if "not set" in field:
            return None
        return dateutil.parser.parse(field).date()
    except:
        return None


def parse_row(row):
    return {
        'title': get_title(row),
        'author': get_author(row),
        'link': get_link(row),
        'pages': get_num_pages(row),
        'date_started': get_date(row, "date_started"),
        'date_read': get_date(row, "date_read"),
        'date_added': get_date(row, "date_added"),
    }


def get_books_page(user, shelf=None, page=0, max_retries=10):
    ua = UserAgent(platforms="desktop")

    params = {
        "v": 2,
        "id": user,
    }
    if shelf is not None:
        params["shelf"] = shelf
    if page is not None and page != 0:
        params["page"] = page

    url = "https://www.goodreads.com/review/list"
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml",
        "Host": "www.goodreads.com",
        "User-Agent": ua.random,
    }

    print("Retrieving books (shelf {}, page {})...".format(shelf, page))

    response = requests.get(url, params, headers=headers)

    # Implement retries (goodreads tends to not be stable)
    retries = 0
    while response.status_code != 200 and retries < max_retries:
        print("Error retrieving books (shelf {}, page {}): status code {}".format(
            shelf, page, response.status_code))
        print("")
        print("Response headers: {}".format(response.headers))
        print("")
        print("Response body: {}".format(response.content))

        time.sleep(1)

        print("")
        print("Retry n. {}".format(retries+1))
        response = requests.get(url, params, headers=headers)
        retries += 1
    if retries >= max_retries:
        raise Exception("Error retrieving books, status code {}")

    content = response.content.decode('utf-8')
    soup = BeautifulSoup(content, "html.parser")
    rows = soup.find_all('tr', class_='review')

    return [parse_row(row) for row in rows]


def get_books(user, shelf):
    books = []
    page = 1
    res = get_books_page(user, shelf, page)
    while len(res) > 0:
        books.extend(res)
        print("Found {} book{} (shelf {}, page {})"
              .format(len(res), plural(res), shelf, page))
        page += 1
        res = get_books_page(user, shelf, page)

    print("Found a total of {} book{}".format(len(books), plural(books)))

    return books


def plural(list: Sized) -> str:
    return "s" if len(list) > 1 else ""

