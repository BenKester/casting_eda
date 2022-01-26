import requests
import urllib.request
from bs4 import BeautifulSoup

class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"

def get_html(url:str, method:str='trad'):
    if method=='old':
        # older method that gives a warning but can get around some security that the newer method can't.
        opener = AppURLopener()
        response = opener.open(url)
        return response
    else:
        with requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as fp:
            return fp.text

def get_soup(url:str, method:str='trad'):
    return BeautifulSoup(get_html(url, method), 'html.parser')
