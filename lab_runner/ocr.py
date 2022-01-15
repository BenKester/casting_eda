import pytesseract
from PIL import Image
import json
import pyautogui
import urllib.request
from bs4 import BeautifulSoup


def load_image(path:str):
    return Image.open(path)

def screenshot():
    return pyautogui.screenshot()

def get_text_from_image(image:Image):
    return pytesseract.image_to_string(image)

def load_enchants():
    with open('enchants.json') as f:
        enchants = json.load(f)
    return enchants

def get_enchants_from_screenshot(warnings:bool = True):
    return get_enchants_from_image(screenshot())

def get_enchants_from_image(image:Image, warnings:bool = True):
    text = get_text_from_image(image).lower()
    enchants = load_enchants()
    ret = {}
    for gear in enchants:
        ret[gear] = []
        for enchant in enchants[gear]:
            if enchant[5:45].lower() in text:
                ret[gear].append(enchant)

    if warnings:
        expected = {'helmet': 3, 'gloves': 1, 'boots': 1}
        for k, v in expected.items():
            if len(ret[k]) != v:
                print(f'Expected {v} {k}, got {len(ret[k])}')

    return ret
