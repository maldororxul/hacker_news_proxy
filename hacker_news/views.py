"""Views handlers for Hacker News proxy"""
__author__ = 'ke.mizonov'
import re
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from dataclasses import dataclass, field
from django.http import Http404, HttpRequest, HttpResponse
from django.http.response import HttpResponseNotFound
from .constants import BASE_URL, REPLACEMENT_PATTERN, TRADEMARK


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
            modified = modified.replace(word, f'{word}{suffix}')
        elem.string.replace_with(modified)

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
        if response.status_code == HttpResponseNotFound:
            raise Http404
        return response

    @classmethod
    def __modify_html_data(cls, response: requests.Response) -> bytes:
        """Modifies HTML-content

        Args:
            response: HTML-response from the source

        Returns:
            Modified data
        """
        soup = BeautifulSoup(response.text, 'lxml')
        for elem in soup.find_all(text=REPLACEMENT_PATTERN) or []:
            cls.__append_suffix_by_pattern(elem=elem, pattern=REPLACEMENT_PATTERN, suffix=TRADEMARK)
        return soup.prettify("utf-8")
