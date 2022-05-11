"""Constants for Hacker News proxy"""
import re
__author__ = 'ke.mizonov'

BASE_URL = 'https://news.ycombinator.com'
HOME_PAGE = ''
REPLACEMENT_PATTERN = re.compile(r'\b[a-zA-Z]{6}\b')
TRADEMARK = u'\u2122'
