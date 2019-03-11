# -*- coding: utf-8 -*-

import asyncio
import textwrap
import aiohttp

from constants import MONTH_MAPPING, MONTH_MAPPING_INFINITIVE, DELIMITER, SOURCES, EMODJI
from dao import get_airport_by_iata_code


class SkyScannerInterface(object):
    def __init__(self, bitly_token, urls_to_convert, sources=SOURCES, only_site=False):
        self.sources = sources
        self.bitly_token = bitly_token
        self.urls_to_convert = urls_to_convert
        self.url = True
        self.only_site = only_site

    def detect_city_or_raise_exception(self, iata_code):
        city = get_airport_by_iata_code(iata_code)
        if city:
            return city
        else:
            raise KeyError('No such IATA code in our db, please add it manually and retry generate links')

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
        generated_links = ["\n Links for {} are: \n".format(source), ]
        for _url in self.urls_to_convert:
            async with aiohttp.ClientSession() as session:
                shorten_url = await self.short_url(session, url + _url)
                shorten_url = shorten_url['data']['url']

            city_from = self.detect_city_or_raise_exception(self.detect_part_url(_url, 3))
            city_to = self.detect_city_or_raise_exception(self.detect_part_url(_url, 4))
            date_from = self.detect_date(self.detect_part_url(_url, 5))
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
                generated_links.append(
                    '<p> - {0} <a target="_blank" href="{1}">{1}</a></p>'.format(text_for_tg_and_site, shorten_url))
            elif source == 'FB':
                generated_links.append(next(EMODJI) + text)
            else:
                generated_links.append('{} <a href="{}">{}</a>'.format(next(EMODJI), shorten_url, text_for_tg_and_site))
        return generated_links

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
