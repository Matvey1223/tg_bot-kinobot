import asyncio
import json
import re
import time
from typing import List, Optional
import aiohttp
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent
from pydantic import BaseModel


BASE_URL = 'https://lordfilms.vin/'
USER_AGENT = UserAgent().random
API_URL = 'https://stage.plapi.cdnvideohub.com/api/v1/player/sv'
ORIGIN = 'stage.plapi.cdnvideohub.com'
REFERRER = 'https://stage.plapi.cdnvideohub.com/'
PROXY_AIO = "http://tCK8B8:EPNeYv@84.21.162.112:8000"
def searching_film(title: str) -> List[dict]:
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': BASE_URL,
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': BASE_URL,
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }

    params = {
        'do': 'search',
    }

    data = {
        'do': 'search',
        'subaction': 'search',
        'search_start': '0',
        'full_search': '0',
        'result_from': '1',
        'story': title,
    }
    response = requests.post(f'{BASE_URL}index.php', params=params, headers=headers, data=data)
    soup = BeautifulSoup(response.text, 'html.parser')
    urls = [i.get('href') for i in soup.find_all('a', class_='th-in with-mask')]
    titles = [i.text for i in soup.find_all('div', class_='th-title')]
    images = [i.find_next('img').get('src') for i in soup.find_all('div', class_ = 'th-img img-resp-vert')]
    result = []
    for i in range(len(titles)):
        result.append({'title': titles[i], 'url': urls[i], 'img': BASE_URL[:-1] + images[i]})
    return result

def get_film_page(url: str) -> str:
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }

    response = requests.get(
        url=url,
        headers=headers,
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    neccessary_divs = soup.find_all('div', class_='tabs-b video-box')
    args = []
    for div in neccessary_divs:
        pattern = r'<script\s+[^>]*aggr="([^"]+)"\s+aggr_id="([^"]+)"\s+[^>]*pub_id="([^"]+)"\s+[^>]*src="([^"]+)"'
        match = re.search(pattern, str(div))
        args.append(match)
    args = [i for i in args if i != None]
    aggr = args[0].group(1)
    aggr_id = args[0].group(2)
    pub_id = args[0].group(3)
    return aggr, aggr_id, pub_id

class Film(BaseModel):
    hlsUrl: Optional[str] = None
    dashUrl: Optional[str] = None
    mpegQhdUrl: Optional[str] = None
    mpeg2kUrl: Optional[str] = None
    mpeg4kUrl: Optional[str] = None
    mpegHighUrl: Optional[str] = None
    mpegFullHdUrl: Optional[str] = None
    mpegMediumUrl: Optional[str] = None
    mpegLowUrl: Optional[str] = None
    mpegLowestUrl: Optional[str] = None
    mpegTinyUrl: Optional[str] = None

class OneFilmJson(BaseModel):
    sources: Film
    thumbUrl: str
    unitedVideoId: int
    duration: int
    failover_host: str

class ListFilms(BaseModel):
    films: Optional[list[OneFilmJson]] = None

def get_links_on_host(url: str) -> ListFilms:
    aggr, aggr_id, pub_id = get_film_page(url)
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Host': ORIGIN,
        'Origin': BASE_URL,
        'Pragma': 'no-cache',
        'Referer': url,
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'pub': pub_id,
        'id': aggr_id,
        'aggr': aggr,
    }

    response = requests.get(API_URL, params=params, headers=headers)
    json_ = {'films': json.loads(response.text)['video']}
    result = ListFilms(**json_)
    print(result)
    return result

def get_qualities(films: ListFilms) -> dict:
    result = {}
    for i in films.films:
        if i.sources.hlsUrl:
            result['hlsUrl'] = i.sources.hlsUrl
        if i.sources.mpegFullHdUrl:
            result['fullHd'] = i.sources.mpegFullHdUrl
        if i.sources.mpegHighUrl:
            result['highUrl'] = i.sources.mpegHighUrl
        if i.sources.mpegMediumUrl:
            result['mediumUrl'] = i.sources.mpegMediumUrl
        if i.sources.mpegLowUrl:
            result['lowUrl'] = i.sources.mpegLowUrl
    unique_dict = {k: v for k, v in zip(result.keys(), result.values())}
    print(unique_dict)
    return unique_dict



if __name__ == '__main__':
    pass
    # urls = searching_film('мстители финал')
    # hlsurl = get_links_on_host(urls[0]['url'])
    # asyncio.run(download1('https://ok21-2.vkuser.net/?expires=1733256623682&srcIp=95.105.64.62&pr=90&srcAg=CHROME&ms=94.41.117.4&type=3&sig=LUU0ycrgHzA&ct=0&urls=45.136.20.48%3B45.136.22.14&clientType=46&zs=28&id=6623769397780', '1213', proxy=False))
