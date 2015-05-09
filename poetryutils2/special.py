# coding: utf-8
from __future__ import print_function
from __future__ import unicode_literals


import requests
from bs4 import BeautifulSoup
from collections import namedtuple
import random
import re

Poem = namedtuple('Poem', ['title', 'author', 'lines'])


def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        raw_text = response.text.strip()
        return BeautifulSoup(raw_text)


# this doesn't work because poetryfoundation's random poem url doesn't
# seem to work
def random_poem():
    soup = get_soup(
        'http://www.poetryfoundation.org/widget/single_random_poem')
    if soup:
        poem_link = "http://www.poetryfoundation.org%s" % soup.find(
            "a")["href"]
        full_poem = get_soup(poem_link)
        if full_poem:
            return extract_poem(full_poem)

# this is way more manual, because their nice random function doesn't seem
# to work correctly


def random_poem2():
    total_poems = 12793  # just looked up on
    total_pages = int(total_poems / 20)  # poems per page
    rand = random.randint(0, total_pages)
    random_page = "http://www.poetryfoundation.org/searchresults?page=%s" % rand
    soup = get_soup(random_page)
    links = soup.find_all(href=re.compile(r'poem'))
    links = [l.get("href") for l in links]
    random_link = random.choice(links)
    poem_link = "http://www.poetryfoundation.org%s" % random_link
    return get_poem_at_url(poem_link)


def get_poem_at_url(url):
    print(poem_link)
    full_poem = get_soup(poem_link)
    if full_poem:
        return extract_poem(full_poem)


def extract_poem(soup):
    poem = soup.find(id="poemwrapper")
    title = get_title(poem)
    author = get_author(poem)
    lines = get_lines(poem)

    return Poem(title, author, lines)


def get_title(soup):
    title = soup.find(id="poem-top").h1
    return title.text


def get_author(soup):
    results = soup.find(class_="author")
    return results.a.text.strip()


def get_lines(soup):
    poem = soup.find(id="poem")
    poem = poem.find(class_="poem").find_all("div")
    lines = [l.text for l in poem]
    return lines


def pretty_print_poem(poem):
    return "%s — %s\n\n%s" % (poem.title, poem.author, "\n".join(poem.lines))


def test():
    soup = BeautifulSoup(raw_sample)
    poem = soup.find(id="poemwrapper")

    title = get_title(poem)
    assert title == "Lamenting Widow", "title incorrect: %s" % title

    author = get_author(poem)
    assert author == "Ho Xuan Huong", "author incorrect: %s" % author

    lines = get_lines(poem)
    assert len(lines) == 4

    # random_poem2()
    print(pretty_print_poem(random_poem2()))


# def main():
#     import argparse
    # parser = argparse.ArgumentParser()
#     parser.add_argument('arg1', type=str, help="required argument")
#     parser.add_argument('arg2', '--argument-2', help='optional boolean argument', action="store_true")
#     args = parser.parse_args()


if __name__ == "__main__":
    test()
