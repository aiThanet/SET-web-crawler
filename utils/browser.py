import requests
import requests.utils
import requests.cookies
import asyncio
import aiohttp
from bs4 import BeautifulSoup

import urllib3
urllib3.disable_warnings()

class AsyncBrowser:
    def __init__(self, **kwargs):
        self._user_agent = kwargs.get('user_agent', self._user_agent())
        self._timeout = kwargs.get('timeout', 100)
        self._debug = kwargs.get('debug', False)

    def build_requests(self, **kwargs):
        if self._timeout:
            kwargs['timeout'] = self._timeout

        # if self._debug:
        #     kwargs['verify'] = False
        #     kwargs['proxies'] = {
        #         'http': 'http://127.0.0.1:8080',
        #         'https': 'http://127.0.0.1:8080'
        #     }

        if 'headers' in kwargs:
            if 'User-Agent' not in kwargs['headers']:
                kwargs['headers'].update({
                    'User-Agent' : self._user_agent
                })
        else :
            kwargs['headers'] = {'User-Agent' : self._user_agent}
        
        return kwargs

    async def get(self, **kwargs):
        payload = self.build_requests(**kwargs)
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(**payload, ssl=False) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html5lib')
                # self.print_debug(soup.prettify())
                return soup

    async def post(self, **kwargs):
        payload = self.build_requests(**kwargs)
        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.post(**payload, ssl=False) as response:
                text = await response.text()
                soup = BeautifulSoup(text, 'html5lib')
                # self.print_debug(soup.prettify())
                return soup

    def print_debug(self, text):
        if(self._debug):
            print(text)

    
    @staticmethod
    def _user_agent():
        return ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/79.0.3945.79 Safari/537.36')
  