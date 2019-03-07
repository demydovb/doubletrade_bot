# -*- coding: utf-8 -*-
import os
import asyncio
import itertools
import textwrap
import aiohttp
from dotenv import load_dotenv, find_dotenv

from constants import CITY_MAPPING, MONTH_MAPPING, MONTH_MAPPING_INFINITIVE, DELIMITER, SOURCES, EMODJI


class SkyScannerInterface(object):
    def __init__(self, bitly_token, urls_to_convert, sources=SOURCES, only_site=False):
        self.sources = sources
        self.bitly_token = bitly_token
        self.urls_to_convert = urls_to_convert
        self.url = True
        self.only_site = only_site

    def detect_part_url(self, url, number):
        return url.split(DELIMITER)[number]

    def detect_date(self, raw_date):
        if len(raw_date) != 6:
            return None
        year, month, day = textwrap.wrap(raw_date, 2)
        if day.startswith('0'):
            day = day[-1]
        return "{day} {month}".format(day=day, month=MONTH_MAPPING[str(month)])

    def detect_month_calendar(self, url):
        for params in url.split('&'):
            if params.startswith('oym'):
                return MONTH_MAPPING_INFINITIVE[params[-2:]]

    async def short_url(self, session, url):
        query_params = {
            'access_token': self.bitly_token,
            'longUrl': url
        }
        endpoint = 'https://api-ssl.bitly.com/v3/shorten'

        async with session.get(endpoint, params=query_params) as response:
            return await response.json()

    async def generate_urls(self, source, url):
        text_to_print = ["\n Links for {} are: \n".format(source), ]
        for _url in self.urls_to_convert:
            async with aiohttp.ClientSession() as session:
                shorten_url = await self.short_url(session, url + _url)
                shorten_url = shorten_url['data']['url']
            city_from = CITY_MAPPING.get(self.detect_part_url(_url, 3), "Unknown city")
            city_to = CITY_MAPPING.get(self.detect_part_url(_url, 4), "Unknown city")
            date_from = self.detect_date(self.detect_part_url(_url, 5))
            if date_from == None:
                print('{city_from}-{city_to}. Календар дешевих квитків на {month}  {shorten_url}'.format(
                    city_from=city_from, city_to=city_to,
                    date_from=date_from, shorten_url=shorten_url, month=self.detect_month_calendar(_url)))
                continue

            date_to = self.detect_date(self.detect_part_url(_url, 6))
            if date_from and date_to:
                text_for_tg_and_site = '{city_from}-{city_to}-{city_from} {date_from}-{date_to}'.format(
                    city_from=city_from, city_to=city_to,
                    date_from=date_from, date_to=date_to)
                text = '{} {}'.format(text_for_tg_and_site, shorten_url)
            else:
                text_for_tg_and_site = '{city_from}-{city_to} {date_from}'.format(city_from=city_from, city_to=city_to,
                                                                                  date_from=date_from)
                text = '{} {}'.format(text_for_tg_and_site, shorten_url)

            if source == 'SITE':
                text_to_print.append(
                    '<p> - {0} <a target="_blank" href="{1}">{1}</a></p>'.format(text_for_tg_and_site, shorten_url))
            elif source == 'FB':
                text_to_print.append(next(EMODJI) + text)
            else:
                text_to_print.append('{} <a href="{}">{}</a>'.format(next(EMODJI), shorten_url, text_for_tg_and_site))
        return text_to_print

    async def main(self):
        tasks = (
            self.generate_urls("SITE", SOURCES['SITE']),
            self.generate_urls("FB", SOURCES['FB']),
            self.generate_urls("TG", SOURCES['TG']),
        )
        if self.only_site:
            return await asyncio.gather(tasks[0])
        else:
            return await asyncio.gather(*tasks)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    URL = True
    urls_to_convert = []
    only_site = input('Generate links only for site?')
    while URL:
        URL = input('Please, enter url:')[9:]
        if URL:
            urls_to_convert.append(URL)

    bitly_token = os.getenv('BITLY_TOKEN')
    print(bitly_token)
    skyscanner = SkyScannerInterface(bitly_token, urls_to_convert, only_site)
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(skyscanner.main())

    for url in itertools.chain.from_iterable(result):
        print(url)
