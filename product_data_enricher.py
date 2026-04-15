print("SCRIPT STARTED")
from playwright.async_api import async_playwright, Browser
from playwright_stealth import Stealth
from urllib.parse import urlparse, urlunparse, parse_qs, quote_plus, quote
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from difflib import SequenceMatcher
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
from html import unescape
from telegram import Bot
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import psutil
import sys
import playwright_stealth
import tracemalloc
import time
import gc
import httpx
import requests
import json
import re
import random
import pprint
import time
import html
import os
import unicodedata
import asyncio

sys.stdout.reconfigure(line_buffering=True)

load_dotenv("/etc/secrets/.env")

ALGOLIA_APP_ID = os.getenv("ALGOLIA_APP_ID")
BOT_TOKEN = os.getenv("BOT_TOKEN")
MANAGER_BOT_TOKEN = os.getenv("MANAGER_BOT_TOKEN")
TARGET_GROUP_ID = os.getenv("TARGET_GROUP_ID")
print(ALGOLIA_APP_ID)
print(BOT_TOKEN)
print(MANAGER_BOT_TOKEN)
print(TARGET_GROUP_ID)

PRODUCT_TYPE_TERMS = {
    "Парфум": ["elixir de parfum", "extrait de parfum", "parfum"],
    "Парфумована вода": ["edp"],
    "Туалетна вода": ["edt"],
    "Одеколон": ["edc"],
    "Роликові парфуми": ["roll-on"],
    "Гель для душу": ["sh", "gel"],
    "Лосьйон для тіла": ["b", "lot"],
    "Бальзам після гоління": ["balm"],
    "Лосьйон після гоління": ["lotion"],
    "Дезодорант-стік": ["deo-stick"],
    "Дезодорант-спрей": ["deo-spray"],
}

PRODUCT_TYPE_EXTENDED_TERMS = {
    "Eau de Parfum": ["Парфумована вода"],
    "Eau de Toilette": ["Туалетна вода"],
    "Eau de Cologne": ["Одеколон"],
}

PTT_2 = {
    "Спрей": ["spray"]
}

SPECIAL_MARK_TERMS = {
    "Мініатюра": ["mini", "мініатюра"],
    "Пробник": ["vial", "віалка", "пробник"],
    "Тестер": ["tester", "тестер"],
    "Змінний блок": ["refill"],
}

SEX_TERMS = {
    "для чоловіків": ["чол", "чол.,", "M", "(M)", "man"],
    "для жінок": ["жін", "жін.,", "L", "(L)", "woman"],
    "унісекс": ["унів", "унів.,", "U", "(U)", "unisex", "L/M", "(L/M)", "M/L", "(M/L)", "L\\M", "(L\\M)", "M\\L", "(M\\L)"],
}

AROMA_TYPE_TERMS = {
    "Альдегідні": ["альдегідні", "альдегідний", "альдегіди"],

    "Амброві": ["амброві", "амбровий", "амбра"],

    "Деревні": ["деревні", "деревний", "дерево", "димний", "пачулі", "землистий"],

    "Зелені": ["зелені", "зелений", "трав'янистий"],

    "Морські": ["морські", "морський", "солоний", "мінеральний", "акватичний"],

    "Пряні": ["пряні", "пряний", "свіжо-пряний", "теплий пряний"],

    "Східні": ["східні"],

    "Фруктові": ["фруктові", "фруктовий"],

    "Фужерні": ["фужерні", "фужерний"],

    "Цитрусові": ["цитрусові", "цитрус", "цитрусовий"],

    "Шипрові": ["шипрові", "шипровий"],

    "Шкіряні": ["шкіряні", "шкіряний", "шкіра"],

    "Гурманські": ["гурманські", "гурманський"],

    "Квіткові": [
        "квіткові",
        "квітковий",
        "біло-квітковий",
        "жовто-квітковий",
        "троянда",
        "фіалковий"
    ],

    "М'ятні": ["м'ятні", "м'ятний"],

    "Пудрові": ["пудрові", "пудровий"],

    "Свіжі": ["свіжі", "свіжий", "озоновий"],

    "Солодкі": ["солодкі", "солодкий", "ванільний", "ваніль"]
}

PERFUME_BRANDS = {
    "27 87 Perfumes": ["27 87"],
    "Antonio Banderas": ["A.BANDERAS"],
    "Abercrombie & Fitch": ["A&F"],
    "Acca Kappa": [],
    "Acqua Di Parma": [],
    "Afnan": [],
    "Agent Provocateur": [],
    "Ajmal": [],
    "Akro": [],
    "Al Haramain": ["AL HARAMAIN", "Al Haramain Perfumes"],
    "Alfred Dunhill": ["DUNHILL"],
    "Alviero Martini": [],
    "Amouage": [],
    "Angel Schlesser": [],
    "Anna Sui": [],
    "Ariana Grande": [],
    "Armaf": [],
    "Armand Basi": [],
    "Atelier Cologne": [],
    "Atkinsons": [],
    "Attar": [],
    "Azzaro": [],
    "Banana Republic": [],
    "Baldessarini": [],
    "BDK Parfums": [],
    "Bois 1920": [],
    "Benetton": [],
    "Bill Blass": [],
    "Billie Eilish": [],
    "Boadicea The Victorious": [],
    "BORNTOSTANDOUT": [],
    "Bottega Veneta": [],
    "Boucheron": [],
    "Brioni": [],
    "Britney Spears": [],
    "Brunello Cucinelli": [],
    "Burberry": [],
    "Bvlgari": ["Bvlgari", "BVL"],
    "Byredo": [],
    "Cacharel": [],
    "Calvin Klein": ["CK"],
    "Carner Barcelona": [],
    "Carolina Herrera": [],
    "Cartier": [],
    "Cerruti": [],
    "Chanel": [],
    "Chloe": [],
    "Chopard": [],
    "Dior": ["Christian Dior"],
    "Christian Louboutin": [],
    "Cristiana Bellodi": ["Christiana Bellodi "],
    "Clarins": [],
    "Clinique": [],
    "Clive Christian": [],
    "Creed": [],
    "Davidoff": [],
    "Diptyque": [],
    "Dolce & Gabbana": ["D&G"],
    "Donna Karan DKNY": ["DKNY"],
    "Dsquared2": [],
    "Elie Saab": [],
    "Elizabeth Arden": [],
    "Ella K": [],
    "Escada": [],
    "Escentric Molecules": [],
    "Essential Parfums": [],
    "Estee Lauder": [],
    "Etat Libre d’Orange": ["ETAT LIBRE"],
    "Ex Nihilo": [],
    "Floraiku": ["Floraïku"],
    "Francesca Bianchi": [],
    "Franck Boclet": [],
    "Frapin": [],
    "Frederic Malle": [],
    "Giorgio Armani": ["ARMANI", "EMPORIO ARMANI"],
    "Gian Marco Venturi": [],
    "Givenchy": [],
    "Gritti": [],
    "Gucci": [],
    "Guerlain": [],
    "Guy Laroche": [],
    "Haute Fragrance Company HFC": ["HFC"],
    "Helena Rubinstein": ["H.R"],
    "Hermes": [],
    "Hormone Paris": [],
    "Hugo Boss": [],
    "Initio Parfums Prives": ["INITIO"],
    "Issey Miyake": [],
    "Jacques Bogart": ["BOGART"],
    "Jaguar": [],
    "Jean Paul Gaultier": ["J.P.Gaultier", "JPG"],
    "Jennifer Lopez": [],
    "Jil Sander": ["SUNDER"],
    "Jimmy Choo": [],
    "Jo Malone": [],
    "John Varvatos": [],
    "Joop!": ["JOOP"],
    "Juicy Couture": [],
    "Juliette Has A Gun": ["JHG", "Juliette has a gun"],
    "Kajal": [],
    "Kenzo": [],
    "Kilian": ["By Kilian"],
    "Korloff": [],
    "Laboratorio Olfattivo": [],
    "Lacoste": [],
    "Karl Lagerfeld": [],
    "Lalique": [],
    "Lancome": [],
    "Lanvin": [],
    "Le Labo": [],
    "Lattafa Perfumes": ["LATTAFA"],
    "Liquides Imaginaires": [],
    "Lolita Lempicka": [],
    "Louis Vuitton": [],
    "Maison Crivelli": [],
    "Maison Francis Kurkdjian": ["M.F.KURKDJIAN", "M. F. KURKDJIAN", "Maison Francis Kurkdjian Paris"],
    "Mancera": [],
    "Mandarina Duck": [],
    "Marc Jacobs": [],
    "Masaki Matsushima": [],
    "Marc-Antoine Barrois": [],
    "Marina De Bourbon": ["M. DE BOURBON"],
    "Matiere Premiere": [],
    "Memo Paris": ["Memo"],
    "Mercedes Benz": [],
    "Min New York": [],
    "Montblanc": ["MONT BLANC"],
    "Moncler": [],
    "Montale": [],
    "Moschino": [],
    "Narciso Rodriguez": [],
    "Nasomatto": [],
    "Nicolai Parfumeur Createur": [],
    "Nina Ricci": [],
    "Nishane": [],
    "Ormonde Jayne": [],
    "Orto Parisi": [],
    "Paco Rabanne": [],
    "Paris Hilton": [],
    "Paloma Picasso": [],
    "Parfums De Marly": [],
    "Penhaligon's": ["Penhaligon`s"],
    "Pepe Jeans": [],
    "Philipp Plein": [],
    "Pierre Balmain": [],
    "Prada": [],
    "Profvmvm Roma": [],
    "Ralph Lauren": [],
    "Rasasi": [],
    "Remy Latour": [],
    "Roberto Cavalli": [],
    "Rochas": [],
    "Roja": [],
    "Salvatore Ferragamo": ["FERRAGAMO"],
    "Sarah Jessica Parker": ["S.J.P."],
    "Sarvari Paris": ["Sarvari"],
    "Serge Lutens": [],
    "Sergio Tacchini": [],
    "Shaik": ["Designer Shaik"],
    "Shakira": [],
    "Shiseido": [],
    "Sisley": [],
    "Sol de Janeiro": [],
    "Sospiro": [],
    "Mugler": ["Thierry Mugler"],
    "Thomas Kosmala": [],
    "Tiffany & Co": ["Tiffany, TIFFANY & CO"],
    "Tiziana Terenzi": [],
    "Tom Ford": [],
    "Toskovat'": [],
    "Trussardi": [],
    "Ungaro": [],
    "V Canto": [],
    "Valentino": [],
    "Van Cleef Arpels": ["VAN CLEEF"],
    "Vera Wang": [],
    "Versace": [],
    "Viktor & Rolf": ["Viktor&Rolf"],
    "Victoria’s Secret": ["VICTORIA SECRET"],
    "Vilhelm Parfumerie": [],
    "Xerjoff": [],
    "Yves Saint Laurent": ["YSL"],
    "Zadig & Voltaire": [],
    "Agatho Parfum": [],
    "Astrophil & Stella": [],
    "Atelier Des Ors": [],
    "Bibliotheque De Parfum": [],
    "Cave": [],
    "Comme Des Garcons": [],
    "Dries Van Noten": [],
    "Filippo Sorcinelli": [],
    "Fragrance Du Bois": [],
    "Franck Olivier": [],
    "Fugazzi": [],
    "Genyum": [],
    "Giardini Di Toscana": [],
    "Gleam": [],
    "Goldfield & Banks Australia": [],
    "L’Arc": [],
    "Le Persona": [],
    "Lorenzo Pazzaglia": [],
    "M. Micallef": [],
    "Maison Mataha": [],
    "Maison Rebatchi": [],
    "Maison Tahite": [],
    "Maison Martin Margiela": ["Maison Margiela", "MAISON MARJIELA", "Maison Martin Marjiela"],
    "Mexx": [],
    "Milano Fragranze": [],
    "New Notes": [],
    "Orlov Paris": [],
    "Pana Dora": [],
    "Parle Moi De Parfum": [],
    "Philly & Phill": [],
    "Reinvented": [],
    "Room 1015": [],
    "Sensatio Paris": [],
    "Signature": [],
    "Simone Andreoli": [],
    "Spirit Of Kings": [],
    "State Of Mind": [],
    "Stephane Humbert Lucas 777": [],
    "The Gate Fragrances": [],
    "Widian": [],
    "Zeromolecole": [],
    "Zarkoperfume": [],
}

CLASSIFICATION = {
  "27 87 Perfumes": "Нішева",
  "Abercrombie & Fitch": "Елітна",
  "Acca Kappa": "Нішева",
  "Acqua Di Parma": "Нішева",
  "Afnan": "Елітна",
  "Agent Provocateur": "Елітна",
  "Agatho Parfum": "Нішева",
  "Ajmal": "Нішева",
  "Akro": "Нішева",
  "Al Haramain": "Нішева",
  "Alfred Dunhill": "Елітна",
  "Alviero Martini": "Елітна",
  "Amouage": "Нішева",
  "Angel Schlesser": "Елітна",
  "Anna Sui": "Елітна",
  "Antonio Banderas": "Елітна",
  "Ariana Grande": "Елітна",
  "Armaf": "Елітна",
  "Armand Basi": "Елітна",
  "Astrophil & Stella": "Нішева",
  "Atelier Cologne": "Нішева",
  "Atelier Des Ors": "Нішева",
  "Atkinsons": "Нішева",
  "Attar": "Нішева",
  "Azzaro": "Елітна",
  "BDK Parfums": "Нішева",
  "Baldessarini": "Елітна",
  "Banana Republic": "Елітна",
  "Benetton": "Елітна",
  "Bibliotheque De Parfum": "Нішева",
  "Bill Blass": "Елітна",
  "Billie Eilish": "Елітна",
  "Bois 1920": "Нішева",
  "Boadicea The Victorious": "Нішева",
  "BORNTOSTANDOUT": "Нішева",
  "Bottega Veneta": "Елітна",
  "Boucheron": "Елітна",
  "Brioni": "Елітна",
  "Britney Spears": "Елітна",
  "Brunello Cucinelli": "Нішева",
  "Burberry": "Елітна",
  "Bvlgari": "Елітна",
  "Byredo": "Нішева",
  "Cacharel": "Елітна",
  "Calvin Klein": "Елітна",
  "Carner Barcelona": "Нішева",
  "Carolina Herrera": "Елітна",
  "Cartier": "Елітна",
  "Cave": "Нішева",
  "Cerruti": "Елітна",
  "Chanel": "Елітна",
  "Chloe": "Елітна",
  "Chopard": "Елітна",
  "Christian Louboutin": "Елітна",
  "Clarins": "Елітна",
  "Clinique": "Елітна",
  "Clive Christian": "Нішева",
  "Comme Des Garcons": "Нішева",
  "Creed": "Нішева",
  "Cristiana Bellodi": "Нішева",
  "Davidoff": "Елітна",
  "Dior": "Елітна",
  "Diptyque": "Нішева",
  "Dolce & Gabbana": "Елітна",
  "Donna Karan DKNY": "Елітна",
  "Dries Van Noten": "Нішева",
  "Dsquared2": "Елітна",
  "Elie Saab": "Елітна",
  "Elizabeth Arden": "Елітна",
  "Ella K": "Нішева",
  "Escada": "Елітна",
  "Escentric Molecules": "Нішева",
  "Essential Parfums": "Нішева",
  "Estee Lauder": "Елітна",
  "Etat Libre d’Orange": "Нішева",
  "Ex Nihilo": "Нішева",
  "Filippo Sorcinelli": "Нішева",
  "Floraïku": "Нішева",
  "Franck Boclet": "Нішева",
  "Franck Olivier": "Елітна",
  "Francesca Bianchi": "Нішева",
  "Fragrance Du Bois": "Нішева",
  "Frapin": "Нішева",
  "Frederic Malle": "Нішева",
  "Fugazzi": "Нішева",
  "Genyum": "Нішева",
  "Giardini Di Toscana": "Нішева",
  "Gian Marco Venturi": "Елітна",
  "Giorgio Armani": "Елітна",
  "Givenchy": "Елітна",
  "Gleam": "Нішева",
  "Goldfield & Banks Australia": "Нішева",
  "Gritti": "Нішева",
  "Gucci": "Елітна",
  "Guerlain": "Елітна",
  "Guy Laroche": "Елітна",
  "Haute Fragrance Company HFC": "Нішева",
  "Helena Rubinstein": "Елітна",
  "Hermes": "Елітна",
  "Hormone Paris": "Нішева",
  "Hugo Boss": "Елітна",
  "Initio Parfums Prives": "Нішева",
  "Issey Miyake": "Елітна",
  "Jacques Bogart": "Елітна",
  "Jaguar": "Елітна",
  "Jean Paul Gaultier": "Елітна",
  "Jennifer Lopez": "Елітна",
  "Jil Sander": "Елітна",
  "Jimmy Choo": "Елітна",
  "Jo Malone": "Нішева",
  "John Varvatos": "Елітна",
  "Joop!": "Елітна",
  "Juicy Couture": "Елітна",
  "Juliette Has A Gun": "Нішева",
  "Kajal": "Нішева",
  "Karl Lagerfeld": "Елітна",
  "Kenzo": "Елітна",
  "Kilian": "Нішева",
  "Korloff": "Елітна",
  "L’Arc": "Нішева",
  "Laboratorio Olfattivo": "Нішева",
  "Lacoste": "Елітна",
  "Lalique": "Елітна",
  "Lancome": "Елітна",
  "Lanvin": "Елітна",
  "Lattafa Perfumes": "Елітна",
  "Le Labo": "Нішева",
  "Le Persona": "Нішева",
  "Liquides Imaginaires": "Нішева",
  "Lolita Lempicka": "Елітна",
  "Lorenzo Pazzaglia": "Нішева",
  "Louis Vuitton": "Елітна",
  "M. Micallef": "Нішева",
  "Maison Crivelli": "Нішева",
  "Maison Francis Kurkdjian": "Нішева",
  "Maison Mataha": "Нішева",
  "Maison Martin Margiela": "Нішева",
  "Maison Rebatchi": "Нішева",
  "Maison Tahite": "Нішева",
  "Mancera": "Нішева",
  "Mandarina Duck": "Елітна",
  "Marc Jacobs": "Елітна",
  "Marc-Antoine Barrois": "Нішева",
  "Marina De Bourbon": "Елітна",
  "Masaki Matsushima": "Елітна",
  "Matiere Premiere": "Нішева",
  "Memo Paris": "Нішева",
  "Mercedes Benz": "Елітна",
  "Mexx": "Елітна",
  "Milano Fragranze": "Нішева",
  "Min New York": "Нішева",
  "Moncler": "Елітна",
  "Montale": "Нішева",
  "Montblanc": "Елітна",
  "Moschino": "Елітна",
  "Mugler": "Елітна",
  "Narciso Rodriguez": "Елітна",
  "Nasomatto": "Нішева",
  "New Notes": "Нішева",
  "Nicolai Parfumeur Createur": "Нішева",
  "Nina Ricci": "Елітна",
  "Nishane": "Нішева",
  "Orlov Paris": "Нішева",
  "Ormonde Jayne": "Нішева",
  "Orto Parisi": "Нішева",
  "Paco Rabanne": "Елітна",
  "Paloma Picasso": "Елітна",
  "Pana Dora": "Нішева",
  "Paris Hilton": "Елітна",
  "Parfums De Marly": "Нішева",
  "Parle Moi De Parfum": "Нішева",
  "Penhaligon’s": "Нішева",
  "Pepe Jeans": "Елітна",
  "Philly & Phill": "Нішева",
  "Philipp Plein": "Елітна",
  "Pierre Balmain": "Елітна",
  "Prada": "Елітна",
  "Profvmvm Roma": "Нішева",
  "Ralph Lauren": "Елітна",
  "Rasasi": "Нішева",
  "Reinvented": "Нішева",
  "Remy Latour": "Елітна",
  "Roberto Cavalli": "Елітна",
  "Rochas": "Елітна",
  "Roja": "Нішева",
  "Room 1015": "Нішева",
  "Salvatore Ferragamo": "Елітна",
  "Sarah Jessica Parker": "Елітна",
  "Sarvari Paris": "Нішева",
  "Sensatio Paris": "Нішева",
  "Serge Lutens": "Нішева",
  "Sergio Tacchini": "Елітна",
  "Shaik": "Нішева",
  "Shakira": "Елітна",
  "Shiseido": "Елітна",
  "Signature": "Нішева",
  "Simone Andreoli": "Нішева",
  "Sisley": "Елітна",
  "Sol de Janeiro": "Елітна",
  "Sospiro": "Нішева",
  "Spirit Of Kings": "Нішева",
  "State Of Mind": "Нішева",
  "Stephane Humbert Lucas 777": "Нішева",
  "The Gate Fragrances": "Нішева",
  "Thomas Kosmala": "Нішева",
  "Tiffany": "Елітна",
  "Tiziana Terenzi": "Нішева",
  "Tom Ford": "Нішева",
  "Trussardi": "Елітна",
  "Ungaro": "Елітна",
  "V Canto": "Нішева",
  "Valentino": "Елітна",
  "Van Cleef Arpels": "Нішева",
  "Vera Wang": "Елітна",
  "Versace": "Елітна",
  "Viktor & Rolf": "Елітна",
  "Victoria’s Secret": "Елітна",
  "Vilhelm Parfumerie": "Нішева",
  "Widian": "Нішева",
  "Xerjoff": "Нішева",
  "Yves Saint Laurent": "Елітна",
  "Zadig & Voltaire": "Елітна",
  "Zarkoperfume": "Нішева",
  "Zeromolecole": "Нішева"
}

FRAGRANTICA_BRANDS = {
    "Viktor & Rolf": "Viktor&Rolf",
    "Kilian": "By Kilian",
    "Floraïku": "Floraiku",
    "Lacoste ": "Lacoste Fragrances",
    "Liquides Imaginaires": "Les Liquides Imaginaires",
    "Mercedes Benz": "Mercedes-Benz",
    "Paco Rabanne": " Rabanne",
    "27 87 Perfumes": "27 87",
}

MAKEUP_BRANDS = {
    "Memo Paris": "Memo",
    "Haute Fragrance Company HFC": "Haute Fragrance Company",
    "Paco Rabanne": "Rabanne"
}

UKR_TO_RU = {
    "Парфум": "Духи",
    "Парфуми": "Духи",
    "Парфумована вода": "Парфюмированная вода",
    "Туалетна вода": "Туалетная вода",
    "Одеколон": "Одеколон",
    "Роликові парфуми": "Роликовые духи",
    "Гель для душу": "Гель для душа",
    "Лосьйон для тіла": "Лосьон для тела",
    "Бальзам після гоління": "Бальзам после бритья",
    "Лосьйон після гоління": "Лосьон после бритья",
    "Дезодорант-стік": "Дезодорант-стик",
    "Дезодорант-спрей": "Дезодорант-спрей",
    "Мініатюра": "Миниатюра",
    "Пробник": "Пробник",
    "Тестер": "Тестер",
    "Змінний блок": "Сменный блок",
    "для чоловіків": "для мужчин",
    "для жінок": "для женщин",
    "унісекс": "унисекс",
}

#CATEGORY_NAMES = {
    #"366": "Прайс1 додано в 2",
    #"365": "Прайс2 додано в 1",
    #"339": "Прайс 1 ОПУБЛІКОВАНО Розетка",
    #"352": "Прайс 2 Опубліковано Розетка",
    #"274": "Прайс 1 ОПУБЛІКОВАНО Розетка+Пром",
    #"381": "Прайс 2 Опубліковано Розетка + Пром",
    #"294": "Прайс 1 Не додані (немає)",
    #"383": "Прайс 2 не додані (немає)",
    #"254": "Прайс1",
    #"255": "Прайс2",
#}

LIMIT = 400 * 1024 * 1024  # 400 MB

_self_process = psutil.Process(os.getpid())

async def monitor_memory():
    try:
        while True:
            mem = _self_process.memory_info().rss

            if mem > LIMIT:
                print("WARNING: nearing memory limit", flush=True)

            print(mem, flush=True)

            await asyncio.sleep(1)

    except asyncio.CancelledError:
        print("Memory monitor stopped", flush=True)
        raise


@asynccontextmanager
async def fresh_browser():
    """Yields a single Chromium browser, guaranteed closed on exit."""
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(
        headless=True,
        args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ]
    )
    try:
        yield browser
    finally:
        await browser.close()
        await playwright.stop()

_browser: Browser | None = None
_playwright = None
_browser_lock = asyncio.Lock()

async def get_browser() -> Browser:
    global _browser, _playwright
    async with _browser_lock:
        if _browser is None or not _browser.is_connected():
            _playwright = await async_playwright().start()
            _browser = await _playwright.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",  # most important for Render
                    "--disable-gpu",
                    # Remove --single-process and --no-zygote
                ]
            )
    return _browser

async def close_browser():
    """Call this on app shutdown."""
    global _browser, _playwright
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None

KEEPIN_BASE = "https://api.keepincrm.com/v1"

def keepin_headers():
        return {"X-Auth-Token": os.getenv("CRM_AUTH_TOKEN"), "Accept": "application/json"}

async def send_errors_to_telegram(errors, bot_token, chat_id, debug):
    if errors and debug:
        bot = Bot(token=bot_token)
        print("SENDING MESSAGE")
        try:
            await bot.send_message(
                chat_id=chat_id,
                text="\n".join(debug) + "\n⚠️Помилки⚠️\n\n" + "\n".join(errors)
            )
        except Exception as e:
            print("Failed to send message:", e)

async def get_product_and_id_from_text(text):
    # Extract product name
    product_match = re.search(
        r'назва\s*[:=()]?\s*(.+)',
        text,
        re.IGNORECASE
    )

    # Extract identifier
    id_match = re.search(
        r'id\s*[:=()]?\s*(\d+)',
        text,
        re.IGNORECASE
    )
    return product_match.group(1).strip() if product_match else None, id_match.group(1) if id_match else None

async def get_id_and_urls_from_text(text):
    # Extract product name
    product_match = re.search(
        r'назва\s*[:=()]?\s*(.+)',
        text,
        re.IGNORECASE
    )

    # Extract identifier
    id_match = re.search(
        r'id\s*[:=()]?\s*(\d+)',
        text,
        re.IGNORECASE
    )

    makeup_url = re.search(
        r'makeup url\s*[:=()]?\s*(https?://\S+)',
        text,
        re.IGNORECASE
    )

    fragrantica_url = re.search(
        r'fragrantica url\s*[:=()]?\s*(https?://\S+)',
        text,
        re.IGNORECASE
    )

    randewoo_url = re.search(
        r'randewoo url\s*[:=()]?\s*(https?://\S+)',
        text,
        re.IGNORECASE
    )

    return product_match.group(1).strip() if product_match else None, id_match.group(1) if id_match else None, makeup_url.group(1) if makeup_url else None, fragrantica_url.group(1) if fragrantica_url else None, randewoo_url.group(1) if randewoo_url else None



async def main_func(browser, product, price, sku, identifier, category_id, makeup_url, fragrantica_url, randewoo_url):
    try:
        data = {}
        data["orighinalnost_360"] = "оригинал"
        errors = []
        debug_message = []
    
        def normalize(text):
            if not text:
                return ""
            
            text = unicodedata.normalize("NFKD", str(text))
            text = text.lower()
            text = re.sub(r"[''`]", "", text)
            text = re.sub(r"\s*&\s*", "", text)  # remove & and surrounding spaces
            text = re.sub(r"[^a-zа-яёіїєґ0-9 ]", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s+", " ", text).strip()
            
            return text
    
        def find_product_url(brand, model, concentration, volume):
            base_url = "https://makeup.com.ua"
            if brand in MAKEUP_BRANDS:
                brand = MAKEUP_BRANDS[brand]
            search_string = f"{brand} {model} {concentration} {volume}"
            print(search_string)
            query = quote_plus(search_string)
            search_url = f"{base_url}/ua/search/?q={query}"
            print(search_url, flush=True)
        
            headers = {"User-Agent": "Mozilla/5.0"}
        
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return None
        
            soup = BeautifulSoup(response.text, "html.parser")
        
            # New selector for product cards
            products = soup.select("div.ProductCard__cardContainer")
            del soup
        
            brand_norm = re.sub(r"[''`\u2019\u2018]", "", unicodedata.normalize("NFKD", brand).lower().strip().replace(" ", ""))
            tokens = set(re.sub(r"[''`]", "", model.lower()).split())
        
            for product in products:
                # Title link is now an <a> with class ProductCard__title
                name_tag = product.select_one("a.ProductCard__title")
                if not name_tag:
                    continue
        
                text = unicodedata.normalize("NFKD", name_tag.text)
                text = text.encode("ascii", "ignore").decode()
                product_title = re.sub(r"[''`]", "", text.lower())
        
                # Check brand appears in title
                title_no_spaces = product_title.replace(" ", "")
                if brand_norm not in title_no_spaces:
                    print("SKIPPING BRAND IN MAKEUP PAGE SEARCH", flush=True)
                    continue
        
                print(brand_norm, tokens, product_title, flush=True)
                if not all(token in product_title for token in tokens):
                    continue
        
                href = name_tag.get("href")
                if href:
                    return base_url + href.rstrip("/")
        
            errors.append("Не вдалося знайти makeup.ua url")
            return None
    
        def clean_perfume_name(material_name: str):
            original = material_name.strip()
            material_name_upper = original.upper()
            brand_found = None
    
            for brand, aliases in PERFUME_BRANDS.items():
                # Create a list of things to check: aliases first, then the brand itself
                alias_keys = [alias.upper() for alias in aliases if alias.strip()]  # skip empty
                alias_keys.append(brand.upper())
                alias_keys.sort(key=len, reverse=True)  # longest first
        
                for alias in alias_keys:
                    if material_name_upper.startswith(alias):
                        brand_found = brand
                        # remove the matched alias/brand from the original string
                        original = original[len(alias):].strip()
                        material_name_upper = original.upper()
                        break  # stop after first match
        
                if brand_found:
                    break

    
            # 2️⃣ ---- PHRASE-BASED PRODUCT TYPE DETECTION (NEW) ----
            product_type_found = None
    
            all_product_terms = []
            for category, aliases in PRODUCT_TYPE_TERMS.items():
                for alias in aliases:
                    all_product_terms.append((alias, category))
    
            # 🔥 Sort by length → longest phrases first (CRITICAL)
            all_product_terms.sort(key=lambda x: len(x[0]), reverse=True)
    
            for phrase, category in all_product_terms:
                pattern = re.escape(phrase)
                if re.search(pattern, original):
                    product_type_found = category
    
                    # remove only first occurrence
                    original = re.sub(pattern, '', original, count=1)
                    break
    
            # 3️⃣ Tokenization AFTER phrase removal
            tokens = re.split(r'\s+|[()|]', original)
    
            # Flatten special terms
            special_terms = []
            for term_dict in [SPECIAL_MARK_TERMS, SEX_TERMS, PTT_2]:
                for aliases in term_dict.values():
                    special_terms.extend(aliases)
    
            special_terms = {t.lower() for t in special_terms}
    
            cleaned_tokens = []
    
            i = 0
            while i < len(tokens):
                token = tokens[i].strip()
                token_lower = token.lower()
    
                if not token_lower:
                    i += 1
                    continue
    
                # ❌ Remove special terms
                if token_lower in special_terms:
                    i += 1
                    continue
    
                # ❌ Remove decimals
                if re.match(r'^\d+[.,]\d+$', token_lower):
                    i += 1
                    continue
    
                # ❌ Remove number + unit (e.g., 100 ml)
                if token_lower.isdigit() and i + 1 < len(tokens) and tokens[i + 1].lower() in ['ml', 'g', 'oz']:
                    i += 2
                    continue
    
                # ❌ Remove standalone units
                if token_lower in ['ml', 'g', 'oz', 'spray', 'new']:
                    i += 1
                    continue
    
                # ❌ Remove combined unit (100ml)
                if re.match(r'^\d+([.,]\d+)?(ml|g|oz)$', token_lower):
                    i += 1
                    continue
    
                cleaned_tokens.append(token.capitalize())
                i += 1
    
            cleaned_name = ' '.join(cleaned_tokens)
    
            # 4️⃣ Errors handling
            if not cleaned_name:
                errors.append("\nНе вдалося визначити серію із назви")
    
            if not brand_found:
                errors.append("\nНе вдалося знайти бренд(можливо його не було взагалі)")
    
            return cleaned_name, brand_found
    
        async def get_algolia_key(browser) -> dict | None:
            result = {}
            got_key = asyncio.Event()
        
            context = await browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            )
            page = await context.new_page()
            await page.route("**/*", lambda route: route.abort()
                if route.request.resource_type in ["image", "stylesheet", "font", "media", "other"]
                else route.continue_()
            )
        
            async def handle_response(response):
                if "algolia.net" in response.url and "queries" in response.url:
                    parsed = urlparse(response.url)
                    params = parse_qs(parsed.query)
                    api_key = params.get("x-algolia-api-key", [None])[0]
                    app_id = params.get("x-algolia-application-id", [None])[0]
                    if api_key and app_id:
                        result["api_key"] = api_key
                        result["app_id"] = app_id
                        got_key.set()
        
            page.on("response", handle_response)
            goto_task = asyncio.ensure_future(
                page.goto("https://www.fragrantica.ua/search/", wait_until="commit")
            )
        
            try:
                await asyncio.wait_for(got_key.wait(), timeout=30)
            except asyncio.TimeoutError:
                print("[ERROR] Timed out waiting for Algolia key")
            finally:
                if not goto_task.done():
                    goto_task.cancel()
                    try:
                        await goto_task
                    except (asyncio.CancelledError, Exception):
                        pass
                await context.close()
        
            return result if result else None
                
        async def find_fragrantica_url(browser, product_name, brand, model, concentration):
            ALGOLIA_API_KEY = None  # initialize first
            creds = await get_algolia_key(browser)
            if creds:
                print("API Key:", creds["api_key"], flush=True)
                ALGOLIA_API_KEY = creds["api_key"]
            else:
                print("Failed to extract Algolia credentials")
                return None
                
            url = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/*/queries"
    
            headers = {
                "X-Algolia-Application-Id": ALGOLIA_APP_ID,
                "X-Algolia-API-Key": ALGOLIA_API_KEY,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://www.fragrantica.ua/"
            }
    
            payload = {
                "requests": [
                    {
                        "indexName": "fragrantica_perfumes",
                        "query": product_name,
                        "params": "hitsPerPage=15"
                    }
                ]
            }
    
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload)
            print("Algolia response status:", response.status_code, flush=True)
    
            try:
                data = response.json()
            except Exception as e:
                print("Failed to parse JSON:", e)
                return None
        
            if "results" not in data or not data["results"]:
                print("No results key in Algolia response:", data)
                return None
        
            hits = data["results"][0].get("hits", [])
            if not hits:
                return None
            normalized_brand = ""
        
            if brand in FRAGRANTICA_BRANDS:
                normalized_brand = normalize(FRAGRANTICA_BRANDS[brand])
            else:
                normalized_brand = normalize(brand)
            # Convert Ukrainian concentration into English term used in Fragrantica
            def map_concentration_to_fragrantica(concentration):
                for eng, ukrainian_list in PRODUCT_TYPE_EXTENDED_TERMS.items():
                    if concentration in ukrainian_list:
                        return eng
                return None  # not found
            
            # ---- inside your function ----
            tokens = set(re.sub(r"[^a-z0-9\s]", "", model.lower()).split())
            
            # map Ukrainian input to English concentration
            fragrantica_concentration = map_concentration_to_fragrantica(concentration)
            extended_tokens = set()
            use_extended = False
            
            if fragrantica_concentration:
                # split English concentration into tokens
                extended_tokens = set(re.sub(r"[’'`]", "", fragrantica_concentration.lower()).split())
                use_extended = True
            
            fallback_candidate = None
            if use_extended:
                for hit in hits:
                    hit_brand = normalize(hit.get("dizajner"))
                    hit_name = normalize(hit.get("naslov"))
                    hit_tokens = set(hit_name.split())
                
                    print(normalized_brand, hit_brand, tokens, hit_tokens, flush=True)
                
                    if normalized_brand != hit_brand:
                        print(f"BRAND MISMATCH: expected '{normalized_brand}' got '{hit_brand}'", flush=True)
                        continue
                
                    expected_tokens = tokens | extended_tokens
                    print("EXPECTED TOKENS:", expected_tokens, flush=True)  # add this
                    
                    if hit_tokens == expected_tokens or hit_tokens == (expected_tokens | set(re.sub(r"[^a-z0-9\s]", "", normalized_brand.lower()).split())):
                        print("MATCHED WITH CONCENTRATION (EXACT)", flush=True)
                        slug = hit.get("slug")
                        website_id = hit.get('id')
                        if slug and website_id:
                            return f"https://www.fragrantica.ua/perfume/{slug}-{website_id}.html"
                        
            for hit in hits:
                hit_brand = normalize(hit.get("dizajner"))
                hit_name = normalize(hit.get("naslov"))
                hit_tokens = set(hit_name.split())
            
                print(normalized_brand, hit_brand, tokens, hit_tokens, flush=True)
            
                if normalized_brand != hit_brand:
                    print(f"BRAND MISMATCH: expected '{normalized_brand}' got '{hit_brand}'", flush=True)
                    continue
                            
                if hit_tokens == tokens or hit_tokens == (tokens | set(re.sub(r"[^a-z0-9\s]", "", normalized_brand.lower()).split())):
                    print("MATCHED TOKENS ONLY (EXACT)", flush=True)
                    slug = hit.get("slug")
                    website_id = hit.get('id')
                    if slug and website_id:
                        return f"https://www.fragrantica.ua/perfume/{slug}-{website_id}.html"
    
        exact_collection = ""
        brand = ""
        url = ""
        RU_url = ""
        debug_message.append(f"id: {identifier}")
        if not fragrantica_url:
            fragrantica_url = ""
        if product:
            debug_message.append(f"Назва: {product}")
            exact_collection, brand = clean_perfume_name(product)
        if brand:
            data["proizvoditiel_265"] = brand
        else:
            return errors, debug_message
        price_num = ""
        if price and float(price.replace(',', '.')):
            price_num = float(price.replace(',', '.'))
        else:
            errors.append("\nНе вдалося знайти прайс в CRM та визначити загальну знижку")
        percentage = round(random.uniform(10, 20), 3)
        result = ""
        if price_num:
            result = round(price_num * (percentage / 100))
            print(price_num)
            data["zaghalna_znizhka_587"] = result
        print(f"Random percentage: {percentage}%")
        print(f"Original: {product} | Brand: {brand} | Exact_collection: {exact_collection}", flush=True)
        if sku:
            print(sku)
        def get_country(sku):
            sku_str = str(sku)
    
            # Map of prefix ranges to countries
            country_map = [
                ("00-13", "США та Канада"),
                ("30-37", "Франція"),
                ("380", "Болгарія"),
                ("383", "Словенія"),
                ("385", "Хорватія"),
                ("387", "Боснія та Герцеговина"),
                ("400-440", "Німеччина"),
                ("460-469", "Росія"),
                ("477", "Литва"),
                ("481", "Білорусь"),
                ("482", "Україна"),
                ("487", "Казахстан"),
                ("489", "Гонконг"),
                ("50", "Велика Британія"),
                ("520", "Греція"),
                ("528", "Ліван"),
                ("529", "Кіпр"),
                ("54", "Бельгія, Люксембург"),
                ("560", "Португалія"),
                ("569", "Ісландія"),
                ("57", "Данія"),
                ("590", "Польща"),
                ("594", "Румунія"),
                ("599", "Угорщина"),
                ("621", "Сирія"),
                ("628", "Саудівська Аравія"),
                ("629", "Об’єднані Арабські Емірати"),
                ("64", "Фінляндія"),
                ("690-693", "Китай"),
                ("70", "Норвегія"),
                ("729", "Ізраїль"),
                ("73", "Швеція"),
                ("76", "Швейцарія"),
                ("783", "Італія"),
                ("80-83", "Італія"),
                ("84", "Іспанія"),
                ("858", "Словаччина"),
                ("859", "Чехія"),
                ("860", "Югославія"),
                ("87", "Нідерланди"),
                ("880", "Корея"),
                ("888", "Сінгапур"),
                ("90-91", "Австрія"),
                ("94", "Нова Зеландія"),
            ]
    
            for prefix_range, country in country_map:
                if "-" in prefix_range:
                    start, end = map(int, prefix_range.split("-"))
                    # Determine number of digits in range
                    n_digits = len(prefix_range.split("-")[0])
                    sku_prefix = int(sku_str[:n_digits])
                    if start <= sku_prefix <= end:
                        return country
                else:
                    n_digits = len(prefix_range)
                    sku_prefix = int(sku_str[:n_digits])
                    if sku_prefix == int(prefix_range):
                        return country
    
            return None
    
        print(type(sku))
        if sku:
            sku_digits = ''.join(filter(str.isdigit, sku))
            print(sku_digits)
            print(len(sku_digits))
            print(sku_digits.startswith("200"))
        if len(sku_digits) < 12 or sku_digits.startswith("200"):
            errors.append(f"дліна sku: {len(sku_digits)}, перші три цифри: {sku_digits[:3]}, будь ласка визначте країну вручну")
        if get_country(sku):
            data["strana_proizvoditiel_tovara_10"] = get_country(sku)
        else:
            errors.append("\nНе вдалося визначити країну продавця")
    
        # --- Step 1: Detect special mark ---
    
        # --- Step 2: Detect product type ---
        product_type = ""
        for ptype, terms in PRODUCT_TYPE_TERMS.items():
            if product:
                if any(term in product for term in terms):
                    product_type = ptype
                    break
        sex = ""
    
        # --- Step 5: Detect volume and convert ml → мл ---
        volume = ""
        if product and re.search(r"(\d+(?:[.,]\d+)?)\s*ml", product, re.IGNORECASE):
            volume_match = re.search(r"(\d+(?:[.,]\d+)?)\s*ml", product, re.IGNORECASE)
            if volume_match:
                volume = f"{volume_match.group(1).replace(',', '.')} мл"
    
        special_mark = ""
        if volume:
            data["obiem_1469363"] = volume
            match = re.search(r"\d+(?:[.,]\d+)?", volume)
            vol_value = float(match.group().replace(",", ".")) if match else None
    
            if vol_value is not None:
                if vol_value < 3:
                    data["format_490"] = "Пробник"
                    special_mark = "Пробник"
                elif 3 <= vol_value <= 25:
                    data["format_490"] = "Мініатюра"
                    special_mark = "Мініатюра"
        else:
            errors.append("Не вдалось визначити поле Объем")
    
        if not special_mark:
            for mark, terms in SPECIAL_MARK_TERMS.items():
                if product:
                    if any(term.lower() in product.lower() for term in terms):
                        special_mark = mark
                        data["format_490"] = mark
                        break
                
        if not special_mark:
            data["format_490"] = "Стандартний"
                
        # --- Step 6: Combine components for UA ---
        name_checkbox = ""
        search_name = ""
        fragrantica_brand = ""
        if brand and exact_collection:
            if brand in FRAGRANTICA_BRANDS:
                fragrantica_brand = FRAGRANTICA_BRANDS[brand]
            else:
                fragrantica_brand = brand
            print(brand, type(brand), flush=True)
            print(fragrantica_brand, type(fragrantica_brand), flush=True)
            if fragrantica_brand in CLASSIFICATION:
                print(fragrantica_brand, CLASSIFICATION[fragrantica_brand])
                data["klassifikatsiia_272"] = CLASSIFICATION[fragrantica_brand]
               
            components = [fragrantica_brand, exact_collection]
            search_name = " ".join([comp for comp in components if comp])
            print(search_name, flush=True)

        async def get_fragrantica_page(browser, url: str) -> BeautifulSoup | None:
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
            )
            page = await context.new_page()
            await page.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            await page.route("**/*", lambda route: route.abort()
                if route.request.resource_type in ["image", "stylesheet", "font", "media", "other"]
                else route.continue_()
            )
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_selector("#perfume-description-content", timeout=30000)
                content = await page.content()
                return BeautifulSoup(content, "html.parser")
            except Exception as e:
                print(f"[ERROR] Failed to fetch {url}: {e}")
                return None
            finally:
                await context.close()  # closes page too
        
        async def fragrantica_scrape(fragrantica_url: str):
            try:
                fragrantica_soup = await get_fragrantica_page(browser, fragrantica_url)
    
                collection = ""
                description_block = ""
                fragrantica_description = ""
                accords = []
                accords_header = ""
                
                if fragrantica_soup:
                    gender_span = fragrantica_soup.find("span", class_=lambda c: c and (
                        all(cls in c for cls in ["text-lg", "md:text-2xl", "whitespace-nowrap"]) and
                        any(cls in c for cls in ["text-blue-600", "text-teal-600", "text-pink-600"])
                    ))
                    if gender_span:
                        classes = gender_span.get("class", [])
                        if "text-blue-600" in classes:
                            sex = "для чоловіків"
                        elif "text-pink-600" in classes:
                            sex = "для жінок"
                        elif "text-teal-600" in classes:
                            sex = "унісекс"
                        if sex:
                            print(f"sex from colors: {sex}", flush=True)
                        
                    collection = fragrantica_soup.find("small", string=re.compile(r"Колекції"))
                    description_block = fragrantica_soup.find("div", id="perfume-description-content")
                    accords_header = fragrantica_soup.find("h6", string=lambda x: x and "основні акорди" in x.lower())
                    del fragrantica_soup
            
                if collection:
                    parent = collection.find_parent("h3")
                    name = parent.get_text(strip=True).replace("Колекції", "").strip()
                    data["sieriia_491"] = name
                    #print("Колекції:", name)
                else:
                    print("Колекції not found", flush=True)
        
                if description_block:
                    fragrantica_description = description_block.get_text(separator=" ", strip=True)
                    print(fragrantica_description, flush=True)
                else:
                    errors.append("Не вдалося знайти опис на fragrantica.ua(для нот та типу аромата")
                    print("Description not found", flush=True)
        
                def format_notes(desc):
                    desc = re.sub(r'\s+', ' ', desc).strip()
                    print("formating", flush=True)
        
                    patterns = {
                        "Верхні ноти": r"(?:верхн(?:і|я)\s+ноти?|початков(?:і|а)\s+ноти?)\s*[:：]?\s*([^\.;]+)",
                        "Ноти серця": r"(?:нот[аи]?\s+серця|серцев(?:і|а)\s+ноти?)\s*[:：]?\s*([^\.;]+)",
                        "Базові ноти": r"(?:базов(?:і|а)\s+ноти?|ноти\s+бази)\s*[:：]?\s*([^\.;]+)"
                    }
        
                    formatted_sections = []
        
                    for key, pattern in patterns.items():
                        match = re.search(pattern, desc, re.IGNORECASE)
                        if match:
                            print(match.group(1))
                            notes = match.group(1)
        
                            # Remove only leading conjunctions like 'а', 'та', 'і' (not part of note names)
                            notes = re.sub(r'^(?:а|та|і)\b\s*:?\s*', '', notes, flags=re.IGNORECASE)
        
                            notes_list = [
                                n.strip().capitalize()
                                for n in re.split(r',|\sі\s|\sта\s', notes)
                                if n.strip()
                            ]
        
                            formatted_sections.append(f"{key}: {', '.join(notes_list)}.")
        
                    return ' '.join(formatted_sections)
        
                required_sections = ["Верхні ноти:", "Ноти серця:", "Базові ноти:"]
        
                def is_valid_notes(text):
                    return all(section in text for section in required_sections)
                
                final_notes = ""
                if fragrantica_description:
                    final_notes = format_notes(fragrantica_description)
                    year = re.search(r'\b(19\d{2}|2\d{3})\b', fragrantica_description)
                    if year:
                        data["god_vypuska_270"] = year.group()
                        print(year.group())
                    print(f"notes 1:{final_notes}", flush=True)
                    print(is_valid_notes(final_notes))
                        
                if final_notes:
                    if is_valid_notes(final_notes):
                        data["noty_446"] = final_notes
                    else:
                        errors.append("У фінальних нотах неправильна структура або їх немає на fragrantica.ua")
                        print("Notes structure is incomplete1:", final_notes)
                else:
                    errors.append("У фінальних нотах неправильна структура або їх немає на fragrantica.ua")
                    print("Notes structure is incomplete2:", final_notes)
        
                mapped_aroma_types = []
                seen = set()
        
                for aroma_type, terms in AROMA_TYPE_TERMS.items():
                    for term in terms:
                        term_lower = term.lower()
        
                        # Find full word matches only (avoid partial word issues)
                        pattern = r'\b' + re.escape(term_lower) + r'\b'
                    
                        if re.search(pattern, fragrantica_description):
        
                            pattern = r'\b' + re.escape(term_lower) + r'\b(?=[\s\.,;]|$)'
        
                            # ❌ Skip if it's followed by "ноти"
                        if re.search(pattern + r'\s+ноти', fragrantica_description, re.IGNORECASE):
                            continue
        
                        if re.search(pattern, fragrantica_description, re.IGNORECASE):
                            if aroma_type not in seen:
                                mapped_aroma_types.append(aroma_type)
                                seen.add(aroma_type)
        
                accords_container = None
        
                if accords_header:
                    accords_container = accords_header.find_next_sibling("div")
        
                if accords_container:
                    accords = [
                        span.get_text(strip=True)
                        for span in accords_container.find_all("span", class_="truncate")
                    ]
        
                result_string_accords = ""
                if accords:
                    print(f"accords raw:{accords}")
        
                    # Merge description aroma types and accord aroma types
                    mapped_types = mapped_aroma_types.copy()  # start with description values
        
                    for accord in accords:
                        accord_lower = accord.lower()
                        for aroma_type, terms in AROMA_TYPE_TERMS.items():
                            for term in terms:
                                if term.lower() in accord_lower:
                                    if aroma_type not in mapped_types:
                                        mapped_types.append(aroma_type)
                                    break
        
                    if mapped_types:
                        # Convert to comma-separated string
                        result_string_accords = ", ".join(mapped_types)
                        if result_string_accords:
                            data["tip_aromata_269"] = result_string_accords
                        else:
                            errors.append("Не вдалося визначити аккорди на fragrantica.ua")
            except Exception as e:
                print(f"[ERROR] fragrantica_scrape failed: {e}")
                
        print(f"FRAGRANTICA{fragrantica_url}", flush=True)
        if search_name and not fragrantica_url:
            fragrantica_url = await find_fragrantica_url(browser, search_name, fragrantica_brand, exact_collection, product_type)
                
        if fragrantica_url:
            debug_message.append(f"fragrantica url: {fragrantica_url}")
            await fragrantica_scrape(fragrantica_url)
            print(fragrantica_url, flush=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                device_scale_factor=1,
                java_script_enabled=True,
            )
            page = await context.new_page()
            try:
                await page.goto(fragrantica_url, wait_until="domcontentloaded", timeout=60000)
                await page.wait_for_function("""
                () => {
                    const cards = document.querySelectorAll('.tw-rating-card > div');
                    return cards.length > 0;
                }""", timeout=45000)
                await page.wait_for_selector('.tw-rating-card .flex.flex-col', timeout=45000)
        
                def parse_number(text):
                    text = text.lower().replace(',', '').strip()
                    if 'k' in text:
                        return int(float(text.replace('k', '')) * 1000)
                    return int(text)
        
                cards = await page.query_selector_all('.tw-rating-card .flex.flex-col')
                print("Number of rating cards found:", len(cards))
        
                ratings_debug = await page.evaluate("""
                () => {
                    const seasons = ['зима', 'весна', 'літо', 'осінь'];
                    const result = [];
                    document.querySelectorAll('span.font-medium').forEach(labelSpan => {
                        const label = labelSpan.innerText.trim().toLowerCase();
                        if (seasons.includes(label)) {
                            const parentDiv = labelSpan.closest('div');
                            if (!parentDiv) return;
                            const valueSpan = parentDiv.querySelector('span.block.font-semibold');
                            const barDiv = parentDiv.querySelector('div[style*="width"]');
                            const value = valueSpan ? parseInt(valueSpan.innerText.trim()) : null;
                            const width = barDiv ? parseFloat(barDiv.style.width.replace("%","")) : null;
                            result.push({label, value, width});
                        }
                    });
                    return result;
                }
                """)
        
                print("Ratings debug info:", ratings_debug)
                ratings = {r['label']: r['width'] for r in ratings_debug}
                if ratings:
                    season_priority = [
                        ('осінь', 'Осінні аромати'),
                        ('літо', 'Літні аромати'),
                        ('зима', 'Зимові аромати'),
                        ('весна', 'Весняні аромати')
                    ]
                    ratings_over_50 = ", ".join(
                        full_label for key, full_label in season_priority
                        if key in ratings and ratings[key] >= 50
                    )
                    print("Filtered Ratings:", ratings, flush=True)
                    if ratings_over_50:
                        print("Seasons with ≥50% width:", ratings_over_50, flush=True)
                        data["siezon_425"] = ratings_over_50
                    else:
                        errors.append("Не вдалося знайти сезони з шириною ≥50%")
                else:
                    errors.append("Не вдалося знайти рейтинги")
        
            except Exception as e:
                print(f"[ERROR] Ratings scrape failed: {e}")
                errors.append("Не вдалося отримати рейтинги з fragrantica.ua")
            finally:
                await context.close()
        else:
            errors.append("Не вдалося знайти fragrantica.ua url")

        if not sex or sex == "":
            for s, terms in SEX_TERMS.items():
                for term in terms:
                    t = term.lower()
        
                    if len(t) == 1 and t.isalpha():  # M, L, U
                        pattern = rf"\({re.escape(t)}\)"
                    elif t.isalpha():  # man, woman
                        pattern = rf"\b{re.escape(t)}\b"
                    else:
                        pattern = re.escape(t)
        
                    if re.search(pattern, product.lower()):
                        sex = s
                        break
                if sex:
                    break

        if sex and product_type:
            if product_type == "Парфум":
                data["vid_parfiumiernoi_produktsii_271"] = "Парфуми"
                if sex in ["для жінок", "унісекс"]:
                    product_type = "Парфуми"
                else:
                    product_type = "Парфум"
            else:
                data["vid_parfiumiernoi_produktsii_271"] = product_type
        else:
            errors.append("Не вдалось визначити поле Вид парфюмерной продукции")

        print(f"product_type: {product_type}", flush=True)
        print(f"special_mark: {special_mark}", flush=True)
        print(f"brand: {brand}", flush=True)
        print(f"exact_collection: {exact_collection}", flush=True)
        print(f"volume: {volume}", flush=True)
        print(f"sex: {sex}", flush=True)
            
        if product_type and sex and brand and exact_collection and volume:
            components = [special_mark, product_type, sex, brand, exact_collection, volume]
            name_checkbox = " ".join([comp for comp in components if comp])
            
        if brand and exact_collection and product_type and volume:
            if makeup_url:
                url = makeup_url
            else:
                url = find_product_url(brand, exact_collection, product_type, volume)
            if url:
                print("Found URL:", url)
                debug_message.append(f"makeup url: {url}")
                RU_url = re.sub(r'/ua/', '/', url, count=1)  # replace only the first occurrence
                print("Found RU URL:", RU_url)
                
        # --- Step 7: Translate to Russian (longest keys first to avoid partial replacements) ---
        def translate_ukr_to_ru(text):
            for ukr in sorted(UKR_TO_RU.keys(), key=len, reverse=True):
                text = text.replace(ukr, UKR_TO_RU[ukr])
            return text
    
        if name_checkbox:
            print(f"Назва checkbox: {name_checkbox}")
            debug_message.append(f"назва Checkbox: {name_checkbox}")
            
            data["nazva_checkbox_1792424"] = name_checkbox
            data["nazva_ua_rozetka_2524400"] = name_checkbox
            if translate_ukr_to_ru(name_checkbox):
                data["nazva_ru_rozetka_2040969"] = translate_ukr_to_ru(name_checkbox)
        else:
            errors.append("Не вдалось визначити поле Назва Checkbox")
    
        headers = {"User-Agent": "Mozilla/5.0"}
        soup = ""
        container = ""
        RU_soup = ""
        RU_container = ""
        fragrantica_soup = ""
        print(url, flush=True)
        if url:
            context = await browser.new_context()
            page = await context.new_page()
            await page.route("**/*", lambda route: route.abort()
                if route.request.resource_type in ["image", "stylesheet", "font", "media", "other"]
                else route.continue_()
            )
            try:
                await page.goto(url, timeout=20000)
                await asyncio.sleep(5)
                html_content = await page.content()
                soup = BeautifulSoup(html_content, "html.parser")
            except Exception as e:
                print(f"[ERROR] Failed to fetch makeup UA url: {e}", flush=True)
            finally:
                await context.close()

        if RU_url:
            context = await browser.new_context()
            page = await context.new_page()
            await page.route("**/*", lambda route: route.abort()
                if route.request.resource_type in ["image", "stylesheet", "font", "media", "other"]
                else route.continue_()
            )
            try:
                await page.goto(url, timeout=20000)
                await asyncio.sleep(5)
                html_content = await page.content()
                RU_soup = BeautifulSoup(html_content, "html.parser")
            except Exception as e:
                print(f"[ERROR] Failed to fetch makeup RU url: {e}", flush=True)
            finally:
                await context.close()

        if randewoo_url:
            context = await browser.new_context()
            page = await context.new_page()
            description_html_ru = None
            try:
                await page.goto(randewoo_url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(15000)
        
                try:
                    scripts_content = await page.eval_on_selector_all(
                        'script[type="application/ld+json"]',
                        "elements => elements.map(e => e.textContent)"
                    )
                    print(f"Found {len(scripts_content)} JSON-LD scripts")
        
                    for i, content in enumerate(scripts_content, 1):
                        try:
                            data2 = json.loads(content)
                            items2 = data2 if isinstance(data2, list) else [data2]
                            for item in items2:
                                if item.get("@type") == "Product":
                                    description_html_ru = unescape(item["description"]).strip()
                                    print("Found randewoo product description!", flush=True)
                                    break
                            if description_html_ru:
                                break
                        except Exception as e:
                            print(f"Script #{i} JSON parse error:", e)
                except Exception as e:
                    print("Error evaluating scripts:", e)
        
            except Exception as e:
                print(f"[ERROR] Failed to fetch randewoo url: {e}")
            finally:
                await context.close()
        
            if description_html_ru:
                soup_desc = BeautifulSoup(description_html_ru, "html.parser")
                for p in soup_desc.find_all("p"):
                    translated_text = GoogleTranslator(source='ru', target='uk').translate(p.get_text())
                    p.string = translated_text
                if soup_desc and str(soup_desc):
                    data["opisaniie_ua_1469370"] = str(soup_desc)
                else:
                    print("couldnt translate ru to ua from randewoo", flush=True)
                del soup_desc
                data["opisaniie_ru_1469371"] = description_html_ru
    
        if soup:
            print("soup exists", flush=True)
            container = soup.select_one(".ProductCharacteristics__content")
        
            if container:
                print("container exists", flush=True)
        
                block = container.select_one('[class*="Html__html"]')
        
                if block:
                    for strong in block.find_all("strong"):
                        label = strong.get_text(strip=True).replace(":", "")
        
                        value = strong.next_sibling
                        if value:
                            value = str(value).strip()
                        else:
                            value = ""
        
                        if label == "Класифікація" and not data.get("klassifikatsiia_272"):
                            data["klassifikatsiia_272"] = value
        
                        if label == "Серія" and not data.get("sieriia_491"):
                            data["sieriia_491"] = value
        
            if not data.get("klassifikatsiia_272"):
                errors.append("Не вдалося визначити Класифікацію")
        
            if not data.get("sieriia_491"):
                errors.append("Не вдалося знайти колекції")
        
            description_html = ""
        
            content_blocks = soup.select(".ProductCharacteristics__content")
        
            if len(content_blocks) >= 1:
                desc_container = content_blocks[1]
                block = desc_container.select_one('[class*="Html__html"]')
                if block:
                    text = block.get_text(" ", strip=True)
                    if "Alcohol," not in text and "Parfum" not in text:
                        paragraphs = block.find_all("p")
                        if paragraphs:
                            description_html = "".join(str(p) for p in paragraphs)
                        elif len(text) > 300:
                            description_html = str(block)
        
            if not randewoo_url and description_html:
                print("found description ua", flush=True)
                data["opisaniie_ua_1469370"] = description_html
        
            del soup
        
        if RU_soup:
            print("ru soup exists", flush=True)
            RU_container = RU_soup.select_one(".ProductCharacteristics__content")
            if RU_container and randewoo_url is None or randewoo_url == "":
                print("finding description ru", flush=True)
                description_html = ""
        
                content_blocks = RU_soup.select(".ProductCharacteristics__content")
        
                if len(content_blocks) >= 1:
                    desc_container = content_blocks[1]
                    block = desc_container.select_one('[class*="Html__html"]')
                    if block:
                        text = block.get_text(" ", strip=True)
                        if "Alcohol," not in text and "Parfum" not in text:
                            paragraphs = block.find_all("p")
                            if paragraphs:
                                description_html = "".join(str(p) for p in paragraphs)
                            elif len(text) > 300:
                                description_html = str(block)
        
                if not randewoo_url and description_html:
                    print("found description ru", flush=True)
                    data["opisaniie_ru_1469371"] = description_html
                    if not data.get("opisaniie_ua_1469370") or not data["opisaniie_ua_1469370"]:
                        try:
                            translated_text = GoogleTranslator(
                                source='ru',
                                target='uk'
                            ).translate(data["opisaniie_ru_1469371"]).strip()
        
                            if translated_text:
                                data["opisaniie_ua_1469370"] = ''.join(
                                    f'<p>{p.strip()}</p>'
                                    for p in translated_text.split('\n\n')
                                    if p.strip()
                                )
                        except Exception:
                            print("couldn't translate from ru to ua", flush=True)
            del RU_soup
        
        if not randewoo_url and data.get("opisaniie_ua_1469370") and data["opisaniie_ua_1469370"] and (not data.get("opisaniie_ru_1469371") or not data["opisaniie_ua_1469370"]):
            try:
                translated_text = GoogleTranslator(
                    source='uk',
                    target='ru'
                ).translate(data["opisaniie_ua_1469370"]).strip()
            
                if translated_text:
                    data["opisaniie_ru_1469371"] = ''.join(
                        f'<p>{p.strip()}</p>'
                        for p in translated_text.split('\n\n')
                        if p.strip()
                    )
            
            except Exception:
                print("couldn't translate from ua to ru", flush=True)

        if not data.get("opisaniie_ua_1469370") and not data["opisaniie_ua_1469370"]:
            errors.append("Не вдалося заповнити ua опис")

        if not data.get("opisaniie_ru_1469371") and not data["opisaniie_ru_1469371"]:
            errors.append("Не вдалося заповнити ru опис")
    
        custom_fields_array = [{"name": k, "value": str(v)} for k, v in data.items() if v is not None]
        print(custom_fields_array)
        print(json.dumps(data, ensure_ascii=False, indent=4), flush=True)
        def update_material(update_data):
            url = f"{KEEPIN_BASE}/materials/{identifier}"
            resp = requests.patch(url, headers=keepin_headers(), json=update_data, timeout=30)
            resp.raise_for_status()  # raise exception if status code >= 400
            return resp.json()
    
        if errors:
            update_data = {"custom_fields": custom_fields_array}
            keepin_response = update_material(update_data)
            print(errors, flush=True)
            print(debug_message)
            return errors, debug_message
        else:
            if category_id:
                update_data = {"category_id": category_id, "custom_fields": custom_fields_array}
            else:
                update_data = {"custom_fields": custom_fields_array}
            keepin_response = update_material(update_data)
    
        
        return None, None
    finally:
        print("Run finished", flush=True)

def get_materials(category_ids):
    all_items = []

    try:
        for category_id in category_ids:
            page = 1

            while True:
                resp = requests.get(
                    f"{KEEPIN_BASE}/materials",
                    headers=keepin_headers(),
                    params={
                        "q[category_id_eq]": category_id,
                        "page": page
                    },
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()

                items = data.get("items", [])
                all_items.extend(items)

                pagination = data.get("pagination", {})
                total_pages = pagination.get("total_pages", 1)

                if page >= total_pages:
                    break

                page += 1

        return {"items": all_items}

    except requests.RequestException as e:
        print("Error fetching materials:", e)
        return {"items": []}

def get_material_by_id(identifier):
    try:
        resp = requests.get(
            f"{KEEPIN_BASE}/materials/{identifier}",
            headers=keepin_headers(),
            params={"id ": identifier},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print("Error fetching material:", e)
        return {}  # safe fallback

def find_by_sku(sku):
    for candidate in (sku, "0" + sku):
        try:
            resp = requests.get(
                f"{KEEPIN_BASE}/materials/sku/{candidate}",
                headers=keepin_headers(),
                params={"material_sku": candidate},
                timeout=30,
            )
            resp.raise_for_status()
            print(resp.json())
            return resp.json()

        except requests.RequestException as e:
            print(f"Not found by SKU {candidate}:", e)

    return []

def delete_material(material_id):
    try:
        resp = requests.delete(
            f"{KEEPIN_BASE}/materials/{material_id}",
            headers=keepin_headers(),
            timeout=120,
        )
        resp.raise_for_status()
        print(f"Deleted material {material_id}")
    except requests.RequestException as e:
        print(f"Error deleting material {material_id}:", e)
        if e.response:
            print("Status:", e.response.status_code)
            print("Body:", e.response.text)
        else:
            print("Error:", e)


def update_material(update_data, material_id):
    try:
        resp = requests.patch(
            f"{KEEPIN_BASE}/materials/{material_id}",
            headers=keepin_headers(),
            json=update_data,
            timeout=30,
        )
        resp.raise_for_status()
        print(f"Updated material {material_id}, new values: {update_data}")
        return resp.json()
    except requests.RequestException as e:
        print(f"Error updatin gmaterial {material_id}:", e)

CHAT_ID = ""

async def run_process(mode):
    await asyncio.to_thread(process, mode)

def process(mode):
    CATEGORY_SOURCE = []
    CATEGORY_HIGHER_PRICE = ""
    NOT_FOUND_AND_NOT_PERSISTENT_CATEGORY = ""
    FINAL_CATEGORY_MAP = {}
    #used_skus_log = []
    if mode == "1":
        CATEGORY_SOURCE = ["389934", "1496143", "1496142", "683545"]
        CATEGORY_HIGHER_PRICE = "366"
        NOT_FOUND_AND_NOT_PERSISTENT_CATEGORY = "294"
        FINAL_CATEGORY_MAP = {352: 339, 381: 274}
    elif mode == "2":
        CATEGORY_SOURCE = ["389935", "1338735", "1338734", "683544"]
        CATEGORY_HIGHER_PRICE = "365"
        NOT_FOUND_AND_NOT_PERSISTENT_CATEGORY = "383"
        FINAL_CATEGORY_MAP = {339: 352, 274: 381}
    else:
        print(f"Unknown mode {mode}", flush=True)
        return

    material_data = get_materials(CATEGORY_SOURCE)
    materials_list = material_data.get("items", [])

    for mat in materials_list:
        sku = mat.get("sku")
        cost = mat.get("cost")
        print(cost, flush=True)
        if not sku:
            continue

        search_sku = ""
        if mode == "1":
            search_sku = sku.split()[0] + " --"
        if mode == "2":
            search_sku = sku.split()[0] + " -"

        if not search_sku:
            continue

        material_id = mat.get("id")
        print(f"material_id: {material_id}", flush=True)
        original_category = mat.get("category_id")

        match = find_by_sku(search_sku)
        
        persistent_value = mat.get('stock_rests', {}).get('16571', {}).get('available', 0)
        persistent = persistent_value > 0
        print(f"persistent: {persistent}, {persistent_value}", flush=True)
        
        if not match:
            if not persistent:
                update_data = {"category_id": NOT_FOUND_AND_NOT_PERSISTENT_CATEGORY}
                print(f"moving to {NOT_FOUND_AND_NOT_PERSISTENT_CATEGORY}, because no match and not persistent", flush=True)
                print("Run finished", flush=True)
                keepin_response = update_material(update_data, material_id)
            continue

        target_category = match.get("category_id")

        if target_category not in FINAL_CATEGORY_MAP.keys():
            print(f"SKU {sku} found in category {target_category}, skipping", flush=True)
            if not persistent:
                update_data = {"category_id": NOT_FOUND_AND_NOT_PERSISTENT_CATEGORY}
                print(f"moving to {NOT_FOUND_AND_NOT_PERSISTENT_CATEGORY}, because not in the right category and not persistent", flush=True)
                print("Run finished", flush=True)
                keepin_response = update_material(update_data, material_id)
            continue
            
        match_id = match.get("id")
        print(f"match_id: {match_id}", flush=True)
        
        persistent_in_target_value = match.get('stock_rests', {}).get('16571', {}).get('available', 0)
        persistent_in_target = persistent_in_target_value > 0
        print(f"persistent_in_target: {persistent_in_target}, {persistent_in_target_value}", flush=True)
        
        try:
            price = float(str(mat.get("price", "0")).replace(",", "."))
        except ValueError:
            print(f"Invalid price for SKU {sku}", flush=True)
            continue  

        try:
            target_price = float(str(match.get("price", "0")).replace(",", "."))
        except ValueError:
            target_price = 0.0

        update_data = None
        final_id = ""

        if not persistent or (persistent_in_target and price >= target_price) and original_category != CATEGORY_HIGHER_PRICE:
            update_data = {"category_id": CATEGORY_HIGHER_PRICE}
            final_id = material_id
            
            #from_cat = CATEGORY_NAMES.get(str(original_category), str(original_category))
            #to_cat = CATEGORY_NAMES.get(str(CATEGORY_HIGHER_PRICE), CATEGORY_HIGHER_PRICE)

            #used_skus_log.append(f"{sku} | {from_cat} → {to_cat}")
            
            print(f"price: {price} is >= target_price: {target_price} moving to ПрайсX додано в X", flush=True)
            
        elif not persistent_in_target or price < target_price:
            final_category = str(FINAL_CATEGORY_MAP.get(target_category))
            if final_category:
                final_id = match_id
                stock_rests = match.get("stock_rests", {})

                stock_rests_attributes = []
                
                for office_id, data in stock_rests.items():
                    stock_rests_attributes.append({
                        "office_id": int(office_id),
                        "available": 10.0 if office_id == "16571" else data.get("available", 0)
                    })

                #from_cat = CATEGORY_NAMES.get(str(original_category), str(original_category))
                #to_cat = CATEGORY_NAMES.get(final_category, final_category)
        
                #used_skus_log.append(f"{search_sku} | {from_cat} → {to_cat}")

                    
                update_data = {"category_id": final_category, "sku": sku, "cost": cost, "stock_rests_attributes": stock_rests_attributes}
                delete_material(material_id)
                print(f"price: {price} is < target_price: {target_price} changing values, deleting the duplicate and moving to {final_category}", flush=True)
                
        if update_data and final_id and update_data != "":
            print("Run finished", flush=True)
            keepin_response = update_material(update_data, final_id)

async def run_main(title, price, sku, identifier, target_id, makeup_url, fragrantica_url, randewoo_url):
    monitor_task = asyncio.create_task(monitor_memory())

    try:
        async with fresh_browser() as browser:
            errors_from_run, debug_message = await main_func(
                browser, title, price, sku, identifier, target_id,
                makeup_url, fragrantica_url, randewoo_url
            )

        gc.collect()
        print(f"Chat id2:{CHAT_ID}")

        if errors_from_run:
            await send_errors_to_telegram(
                errors_from_run, BOT_TOKEN, TARGET_GROUP_ID, debug_message
            )
        else:
            if CHAT_ID and CHAT_ID != "":
                bot = Bot(token=MANAGER_BOT_TOKEN)
                print("SENDING SUCCESS MESSAGE", flush=True)
                try:
                    await bot.send_message(
                        chat_id=CHAT_ID,
                        text="✅Успішно опрацьовано"
                    )
                except Exception as e:
                    print("Failed to send message:", e)

    finally:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass

async def process_category(category_id, target_id):
    material_data = get_materials([category_id])
    materials_list = material_data.get("items", [])

    for material in materials_list:
        try:
            title = material.get("title")
            price = material.get("price")
            sku = material.get("sku")
            identifier = material.get("id")

            print(title)
            print(identifier)

            if title:
                print(material.get("category_id"))
                print(material.get("category"))
                await run_main(title, price, sku, identifier, target_id, None, None, None)
                gc.collect()
                await asyncio.sleep(0.5)

        except Exception as e:
            print(f"Error processing material {material.get('id')}: {e}")

async def run_and_notify(mode):
    await run_process(mode)  # runs sync function in thread

    if CHAT_ID:
        bot = Bot(token=MANAGER_BOT_TOKEN)
        try:
            await bot.send_message(
                chat_id=CHAT_ID,
                text="✅Успішно опрацьовано папки"
            )
        except Exception as e:
            print("Failed:", e)
            
async def trigger_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    user_message = update.message.text
    CHAT_ID = update.effective_chat.id
    print(f"Chat id:{CHAT_ID}")

    text_lower = user_message.lower()

    if user_message == "Старт":
        await update.message.reply_text("✅ Процесс запущено")

        # Run heavy code asynchronously
        asyncio.create_task(action_standart())
    elif user_message == "Старт1":
        await update.message.reply_text("✅ Тест1 запущено")

        # Run heavy code asynchronously
        asyncio.create_task(action_standart("1"))
    elif user_message == "Старт2":
        await update.message.reply_text("✅ Тест2 запущено")

        # Run heavy code asynchronously
        asyncio.create_task(action_standart("2"))
    elif user_message == "Тест":
        await update.message.reply_text("✅ Тест запущено")

    elif "назва" in text_lower and "id" in text_lower and not "makeup url" in text_lower and not "fragrantica url" in text_lower:
        await update.message.reply_text("✅ Сообщение содержит 'Назва' и 'id'")
        
        product, identifier = await get_product_and_id_from_text(user_message)
        print(product, identifier)
        asyncio.create_task(action_manual_name_and_id(product, identifier))
    elif "id" in text_lower and ("makeup url" in text_lower or "fragrantica url" in text_lower or "randewoo url" in text_lower):
        await update.message.reply_text("✅ Сообщение содержит 'id' и 'urls'")
        product, identifier, makeup_url, fragrantica_url, randewoo_url = await get_id_and_urls_from_text(user_message)
        print(product, identifier, makeup_url, fragrantica_url, randewoo_url)
        asyncio.create_task(action_manual_urls(product, identifier, makeup_url, fragrantica_url, randewoo_url))
    elif "опрацювати прайс1" in text_lower:
        await update.message.reply_text("✅ Опрацювання Прайс1 запущено")
        asyncio.create_task(run_and_notify("1"))
                
    elif "опрацювати прайс2" in text_lower:
        await update.message.reply_text("✅ Опрацювання Прайс2 запущено")
        asyncio.create_task(run_and_notify("2"))
                    
async def action_standart(category):
    try:
        if category == "1":
            await process_category(1443408, 403)
        elif category == "2":
            await process_category(1464022, 404)
        else:
            await process_category(1443408, 403)
            await process_category(1464022, 404)
    
        print("Standart process finished")

    except Exception as e:
        print("CRASH in action_standart:", e)
        import traceback
        traceback.print_exc()
    
async def action_manual_urls(product, identifier, makeup_url, fragrantica_url, randewoo_url):
    try:
        material = get_material_by_id(int(identifier))
        price = material.get("price")
        sku = material.get("sku")
        target_id = None
        if material.get("category_id") == 401:
            target_id = 403
        elif material.get("category_id") == 402:
            target_id = 404
        print(material.get("category_id"), target_id)
        if product:
            await run_main(product, price, sku, identifier, target_id, makeup_url, fragrantica_url, randewoo_url)
        else:
            await run_main(material.get("title"), price, sku, identifier, target_id, makeup_url, fragrantica_url, randewoo_url
                              )
    except Exception as e:
        print("CRASH in action_manual_urls:", e)
        import traceback
        traceback.print_exc()

async def action_manual_name_and_id(product, identifier):
    try:
        material = get_material_by_id(int(identifier))
        price = material.get("price")
        sku = material.get("sku")
        target_id = None
        if material.get("category_id") == 401:
            target_id = 403
        elif material.get("category_id") == 402:
            target_id = 404
        print(material.get("category_id"), target_id)
        await run_main(product, price, sku, identifier, target_id, None, None, None)
    except Exception as e:
        print("CRASH in action_manual_name_and_id:", e)
        import traceback
        traceback.print_exc()


def start_manager_bot():
    app = ApplicationBuilder().token(MANAGER_BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, trigger_actions))

    print("Manager bot started")
    app.run_polling()
    
if __name__ == "__main__":
    start_manager_bot()
