"""Views handlers for Hacker News proxy"""
__author__ = 'ke.mizonov'
import os
import re
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from dataclasses import dataclass, field
from django.http import Http404, HttpRequest, HttpResponse
from django.http.response import HttpResponseNotFound
from urllib.request import urlretrieve
from project.settings import BASE_DIR, STATIC_URL
from .constants import (
    BASE_URL,
    CSS_EXT,
    CSS_RESOURCES_PATTERN,
    CSS_URL_PATTERN,
    HOME_PAGE,
    REPLACEMENT_PATTERN,
    TRADEMARK
)


@dataclass(frozen=True)
class HackerNews:
    """Class for Hacker News proxy"""
    base_url: str = field(init=False, default=BASE_URL)

    @classmethod
    def proxy(cls, request: HttpRequest) -> HttpResponse:
        """Handler for any requests to Hacker News proxy app

        Args:
            request: HttpRequest with params came from client

        Returns:
            Modified Response from server
        """
        # get HTML-content from source
        data_from_source = cls.__fetch(request=request)
        # modify it and return
        return HttpResponse(
            content=cls.__modify_html_data(response=data_from_source)
        )

    @classmethod
    def __append_suffix_by_pattern(cls, elem: Tag, pattern: re.Pattern, suffix: str):
        """Find all words inside HTML-element text by RegExp pattern and modify them with suffix

        Args:
            elem: HTML-element
            pattern: RegExp pattern
            suffix: Suffix that will be added to each word satisfying pattern
        """
        modified = elem.text
        # use set to exclude repeatable words
        for word in set(pattern.findall(elem.text)):
            if suffix in word:
                continue
            modified = modified.replace(word, f'{word}{suffix}')
        elem.string.replace_with(modified)

    @classmethod
    def __download_static_file(cls, file: str):
        """Downloads resources

        Args:
            file: file name with extension
        """
        # make dirs and download file
        os.makedirs(os.path.join(BASE_DIR, STATIC_URL), exist_ok=True)
        file = file.split("?")[0]
        file_path = f'{STATIC_URL}{file}'
        # skip files that had already been downloaded (fixme: file updated on source)
        if os.path.isfile(file_path):
            return
        urlretrieve(f'{cls.base_url}/{file}', file_path)
        # css files may contain more resources
        _, ext = os.path.splitext(file_path)
        if ext != CSS_EXT:
            return
        with open(file_path, 'r') as css_file:
            for css_resource in CSS_RESOURCES_PATTERN.findall(css_file.read()):
                css_url = CSS_URL_PATTERN.findall(css_resource)[0].strip('"')
                cls.__download_static_file(file=css_url)

    @classmethod
    def __fetch(cls, request: HttpRequest) -> requests.Response:
        """Makes request to the source with params

        Args:
            request: HttpRequest with params came from client

        Returns:
            Response from the source

        Raises:
            Http404: Page not found
        """
        response = requests.get(url=f'{cls.base_url}{request.path_info}', params=request.GET)
        # handle errors (can be extended with other error cases and prettified with HTML-templates)
        if response.status_code == HttpResponseNotFound.status_code:
            raise Http404
        return response

    @classmethod
    def __handle_resources(cls, soup: BeautifulSoup.text, tag: str, attr: str):
        """Modifies resources by adding base url as attr value (href or src) for specified tag elements in soup

        Args:
            soup: bs4 soup
            tag: tag to seek for in soup
            attr: attr to seek for in soup
        """
        for elem in soup.find_all(tag) or []:
            # download static files (with dirty favicon hack)
            file = elem[attr]
            cls.__download_static_file(file=file)
            elem[attr] = f"{STATIC_URL}{file}"

    @classmethod
    def __modify_html_data(cls, response: requests.Response) -> bytes:
        """Modifies HTML-content

        Args:
            response: HTML-response from the source

        Returns:
            Modified data
        """
        soup = BeautifulSoup(response.text, 'lxml')
        # change words
        for elem in soup.find_all(text=REPLACEMENT_PATTERN) or []:
            cls.__append_suffix_by_pattern(elem=elem, pattern=REPLACEMENT_PATTERN, suffix=TRADEMARK)
        # change imgs, scripts and links to "look at" original site recources
        for tag, attr in (('img', 'src'), ('script', 'src'), ('link', 'href')):
            cls.__handle_resources(soup=soup, tag=tag, attr=attr)
        # change home-page links
        for elem in soup.find_all(href=True) or []:
            if elem['href'] == cls.base_url:
                elem['href'] = HOME_PAGE
        return soup.prettify("utf-8")
