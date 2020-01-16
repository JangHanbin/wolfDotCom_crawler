import requests
from selenium import webdriver
import os
import logging

logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('[ %(levelname)s | %(filename)s: %(lineno)s] %(asctime)s > %(message)s')
file_handler = logging.FileHandler('log.log')
file_handler.setFormatter(formatter)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def chrome_header_to_dict(headers):
    return dict([[h.partition(':')[0].strip(), h.partition(':')[2].strip()] for h in headers.split('\n')])



def access_to(toon_id, episode_num, webtoon_name):

    if not os.path.exists(webtoon_name):
        os.makedirs(webtoon_name)

    url = 'https://wfwf61.com/view?toon={0}&num={1}'.format(toon_id, episode_num)

    headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
    accept-encoding: gzip, deflate, br
    accept-language: en-US,en;q=0.9,ko;q=0.8
    cache-control: max-age=0
    referer: http://wfwf61.com/view?toon={0}&num={1}
    sec-fetch-mode: navigate
    sec-fetch-site: cross-site
    upgrade-insecure-requests: 1
    user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36'''.format(toon_id,episode_num)

    options = webdriver.ChromeOptions()
    options.add_argument('headless')

    with webdriver.Chrome('./chromedriver', options=options) as driver:
        driver.implicitly_wait(60)
        logger.info('Loading resources and cookies via webpage[{0}].'.format(url))
        logger.info('This step maybe take a while...')
        driver.get(url)
        imgs = driver.find_elements_by_tag_name('img')

        result = list()
        for img in imgs:
            if not img.get_attribute('src').endswith('.jpg'):
                continue
            result.append((img.get_attribute('src'), img.get_attribute('alt')))


        if result:
            cookies = dict()
            for cookie in driver.get_cookies():
                cookies[cookie['name']] = cookie['value']

            spec_dir = 'episode {1}'.format(webtoon_name, episode_num)
            if not os.path.exists('./{0}/{1}'.format(webtoon_name,spec_dir)):
                os.makedirs('./{0}/{1}'.format(webtoon_name,spec_dir))
            logger.info('Downloading {0} episode {1} ...'.format(webtoon_name, episode_num))
            for idx, t in enumerate(result):
                res = requests.get(t[0], headers=chrome_header_to_dict(headers), cookies=cookies)
                with open('./{1}/{2}/{0}.jpg'.format(t[1],webtoon_name,spec_dir), 'wb') as file:
                    logger.info('Downloading {0} image part of episode {1} [{2}/{3}] from {4}'.format(webtoon_name,episode_num,idx,len(result), t[0]))
                    file.write(res.content)


if __name__=='__main__':
    toon_id = int(input('Toon ID : '))
    episode_num_start = int(input('Start from Episode : '))
    episode_num_end = int(input('End to Episode : '))
    webtoon_name = input('Webtoon Name : ')

    for episode in range(episode_num_start, episode_num_end+1):
        access_to(toon_id,episode,webtoon_name)

