#! /Users/sugar/.pyenv/versions/py396env/bin/python
"""
@File    :   main.py    
@Contact :   zhangyu@onesight.com

@Modify Time    @Author @Version    @Description
------------    ------- --------    -----------
2023/1/29      zhangyu 1.0         None
"""
import os
import requests
from bs4 import BeautifulSoup
from prettytable import PrettyTable
from conf import get_conf, set_conf
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions

HEADER = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}


def skrbt(key_word, home_page=get_conf('skrbt', 'HOME_PAGE'), cookie=get_conf('skrbt', 'COOKIE')):
    HEADER.update({'referer': home_page, 'cookie': cookie})
    magnet_dict, offset, next_page = search(key_word=key_word, home_page=home_page)
    # 更新配置文件
    set_conf(group='skrbt', name='HOME_PAGE', value=home_page)
    set_conf(group='skrbt', name='COOKIE', value=cookie)

    # 继续选择
    while (chose := input('Chose one to get magnet or type in "n/N" to next page:').lower()) in ('n', 'next'):
        magnet_dict, offset, next_page = search(key_word=key_word, home_page=home_page, magnet_dict=magnet_dict, page=next_page, offset=offset)
    mg = magnet_dict.get(chose)
    while not mg:
        print('Wrone id!!!')
        mg = magnet_dict.get(input('Chose one to get magnet:'))
    return mg, home_page


def search(key_word, home_page, magnet_dict={}, page=1, offset=0):
    soup = BeautifulSoup(requests.get(url=f'{home_page}/search?keyword={key_word}&p={page}', headers=HEADER).content, 'html.parser')
    uls, table, offset_point = soup.find_all('ul', 'list-unstyled'), PrettyTable(['id', 'name', 'size', 'time']), 0
    for i, ul in enumerate(uls):
        ahref = ul.find('a', 'rrt common-link')
        offset_point = offset + i + 1
        table.add_row([
            offset_point,
            ahref.find_all('span')[0].text if len(ahref.find_all('span')) == 1 else ahref.text,
            ul.find('li', 'rrmi').find_all('span')[0].text,
            ul.find('li', 'rrmi').find_all('span')[-1].text
        ])
        magnet_dict.update({str(offset_point): f"{home_page}{ahref.get('href')}"})
    print(table)
    return magnet_dict, offset_point, page + 1


def magnet(magnet_url, home_page=get_conf('skrbt', 'HOME_PAGE')):
    HEADER.update({'referer': f'{home_page}/search'})
    soup = BeautifulSoup(requests.get(url=magnet_url, headers=HEADER).content, 'html.parser')
    magnet_href = soup.find('a', {'id': 'magnet'}).get('href')
    os.system(f"osascript -e 'set the clipboard to \"{magnet_href}\"'")
    return magnet_href


# cookie
def refresh_cookie(home_page):
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    # , options = option
    driver = webdriver.Chrome(executable_path='/Users/sugar/setups/chromedriver')
    driver.get(home_page)

    # time.sleep(5)
    # driver.implicitly_wait(10)

    s = WebDriverWait(driver, 10, 0.5).until(
        expected_conditions.visibility_of_element_located((By.NAME, 'keyword'))
    )
    # s = driver.find_element(by=By.CLASS_NAME, value='search-btn')
    s.click()
    # 获取cookie
    cookie_list = driver.get_cookies()
    cookies = "; ".join([item["name"] + "=" + item["value"] + "" for item in cookie_list])
    print(f'Get cookie succeed. cookie: {cookies}')
    driver.close()
    return cookies


if __name__ == '__main__':
    search_kws = {}
    kwstr = input('Type in key_word(required):')
    kws = kwstr.split(',')
    if len(kws) > 0:
        if hp := input('Type in HOME_PAGE(default in skrbt.ini):'):
            search_kws.update({'home_page': hp})
        if ck := input('Type in COOKIE(default in skrbt.ini):'):
            if ck.lower() in ('r', 'refresh'):
                ck = refresh_cookie(hp or get_conf('skrbt', 'HOME_PAGE'))
            search_kws.update({'cookie': ck})
        for kw in kws:
            if kw:
                search_kws.update({'key_word': kw})
                mgurl, hpurl = skrbt(**search_kws)
                print(f'\033[1;31;40m{magnet(mgurl, hpurl)}\033[0m')
        ctn = input('Continue?(n/N or key_word):')
        while ctn not in ('n', 'N'):
            kws = ctn.split(',')
            if len(kws) > 0:
                for kw in kws:
                    if kw:
                        search_kws.update({'key_word': kw})
                        mgurl, hpurl = skrbt(**search_kws)
                        print(f'\033[1;31;40m{magnet(mgurl, hpurl)}\033[0m')
            else:
                print('No key_word to search!')
            ctn = input('Continue?(n/N or key_word):')
    else:
        print('No key_word to search!')

