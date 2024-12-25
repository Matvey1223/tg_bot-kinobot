from typing import List, Optional
from bs4 import BeautifulSoup
import requests
from fake_useragent import UserAgent


BASE_URL = 'https://lordfilm.black/'
BALANCER_URL = 'https://alocdn.shizahd.pro'
USER_AGENT = UserAgent().random


#TODO обернуть все в класс и связать с lordfilms.py
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
    return result[0]['url']
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
    neccessary_ul = soup.find_all('ul', class_='js-player-tabs player-tabs fx-1')
    neccessary_ul = str(neccessary_ul[0]).split('\n')
    li = None
    for i in neccessary_ul:
        if 'alocdn' in str(i):
            li = i
            break
    url = li.split('data-src="')[1].split('" ')[0]
    print(url)
    return url

def get_video(url: str):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': BASE_URL,
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'iframe',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'cross-site',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
    }
    response = requests.get(
        url=url,
        headers=headers,
    )
    token = url.split('token=')[1]
    token_movie = url.split('token_movie=')[1].split('&')[0]
    id_file = response.text.rfind('id_file')
    fragment = response.text[id_file: id_file+50]
    return token_movie, token, str(fragment).split(',')[0].split(':')[1].replace('"', '')

def get_hls(token_movie: str, token: str, id_file: str, quality: Optional[str] = None):
    headers = {
        'accept': '*/*',
        'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': BALANCER_URL,
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'{BALANCER_URL}/?token_movie={token_movie}&token={token}',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'x-requested-with': 'XMLHttpRequest',
    }

    data = {
        'token': token,
        'av1': 'true',
        'autoplay': '0',
        'audio': '',
        'subtitle': '',
    }
    response = requests.post(f'https://alocdn.shizahd.pro/movie/{id_file}', headers=headers, data=data).json()
    return response

def hls_source_request(hls_url: str):
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': BALANCER_URL,
        'Pragma': 'no-cache',
        'Referer': f'{BALANCER_URL}/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
        'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    response = requests.get(
        hls_url,
        headers=headers,
    )
    new_url = hls_url.replace('master.m3u8', response.text.split('\n')[-3])
    response = requests.get(new_url, headers=headers)
    segments = [i for i in response.text.split('\n') if 'seg' in i]
    return segments

if __name__ == '__main__':
    url = searching_film('субстанция')
    src = get_film_page(url)
    token_movie, token, id_file = get_video(src)
    hls = get_hls(token_movie, token, id_file, '2160')
    print(hls)
    print(hls_source_request(hls))



