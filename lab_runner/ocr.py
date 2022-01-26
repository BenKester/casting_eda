import pytesseract
from PIL import Image
import json
import pyautogui
from data import Aggregated, Config

class OCR:
    def __init__(self):
        self.data = Aggregated()
        self.synonyms = Config()['Synonyms']['OCR to Enchant']

    def load_image(self, path:str):
        return Image.open(path)

    def screenshot(self):
        return pyautogui.screenshot()

    def get_text_from_image(self, image:Image):
        return pytesseract.image_to_string(image)

    def get_enchants_from_screenshot(self, warnings:bool = True):
        return self.get_enchants_from_image(self.screenshot())

    def get_enchants_from_image(self, image:Image, warnings:bool = True):
        text = self.get_text_from_image(image).lower()
        enchants = self.data.keys()
        ret = []
        for enchant in enchants:
            if enchant[5:45].lower() in text:
                ret.append(enchant)
        for synonym in self.synonyms.keys():
            if synonym in text:
                ret.append(self.synonym[synonym])

        if warnings:
            if len(ret) != 5:
                print(f'Expected 5, got {len(ret)}')
                print('Try adding a synonym to the config')
                print(text)

        return ret
