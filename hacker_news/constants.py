"""Constants for Hacker News proxy"""
import re
__author__ = 'ke.mizonov'

BASE_URL = 'https://news.ycombinator.com'
REPLACEMENT_PATTERN = re.compile('\s(\w{6})\s')
TRADEMARK = u'\u2122'
