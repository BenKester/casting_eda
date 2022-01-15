import requests
import urllib.request
from bs4 import BeautifulSoup

class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"

def get_soup(url:str, method:str='trad'):
    if method=='old':
        # older method that gives a warning but can get around some security that the newer method can't.
        opener = AppURLopener()
        response = opener.open(url)
        soup = BeautifulSoup(response)
    else:
        with requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as fp:
            soup = BeautifulSoup(fp.text, 'html.parser')
    return soup