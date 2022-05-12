"""Constants for Hacker News proxy"""
import re
__author__ = 'ke.mizonov'

BASE_URL = 'https://news.ycombinator.com'
CSS_EXT = '.css'
CSS_RESOURCES_PATTERN = re.compile(r"""url\(\"[a-z0-9.]+\"\)""")
CSS_URL_PATTERN = re.compile(r"""\"[a-z0-9.]+\"""")
HOME_PAGE = '/'
REPLACEMENT_PATTERN = re.compile(r'\s?[а-яёА-ЯЁa-zA-Z]{6}\s')
TRADEMARK = u'\u2122'
