"""Constants for Hacker News proxy"""
import re
__author__ = 'ke.mizonov'

BASE_URL = 'https://news.ycombinator.com'
HOME_PAGE = '/'
REPLACEMENT_PATTERN = re.compile(r'\s?[а-яёА-ЯЁa-zA-Z]{6}\s')
TRADEMARK = u'\u2122'
