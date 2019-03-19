from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import json
import pandas as pd
from typing import List, Dict


def get_links(url: str) -> List:
    browser = webdriver.Chrome()
    browser.get(url)
    # Wait 20 seconds for page to load
    timeout = 20
    try:
        WebDriverWait(browser, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME, "angel_image")))
    except TimeoutException:
        print('Timed out waiting for page to load')
        browser.quit()

    links = browser.find_elements_by_class_name("startup-link")
    startup_links = set([link.get_attribute('href') for link in links])
    # print(list(startup_links))
    browser.close()
    return list(startup_links)


def get_startup_name(url: str) -> str:
    first_slice = url.rsplit('/', 1)
    title = first_slice[1]
    normal_title = title.replace('-', ' ')
    return normal_title


def loop_through_links(url: str):
    lst = get_links(url)
    investors = {}
    for link in lst:
        browser = webdriver.Chrome()
        browser.get(link)
        try:
            WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.CLASS_NAME, "founders")))
        except TimeoutException:
            print('Timed out waiting for page to load')
            browser.quit()

        # click 'view all __ past investors'
        view_past_investors = browser.find_element_by_class_name('view_all')
        view_past_investors.click()
        browser.implicitly_wait(10)
        # Selenium hands page source to BeautifulSoup
        html = BeautifulSoup(browser.page_source, 'html.parser')
        div_container = html.find('div', class_="group")
        for ltag in div_container.find_all('li', class_='role'):
            for atag in ltag.find_all('a', {'class': ["profile-link", 'startup-link']}):
                if get_startup_name(link) not in investors:
                    investors[get_startup_name(link)] = [atag.text]
                else:
                    investors[get_startup_name(link)].append(atag.text)
        # Get rid of empty strings in list
        investors[get_startup_name(link)] = list(filter(None, investors[get_startup_name(link)]))

        browser.close()
    # print(investors)

    #create json file
    with open('investors.json', 'w') as file:
        json.dump(investors, file)
        json_obj = 'investors.json'

    # open('investors.json', 'r').read()
    return json_obj


def load_json(url: str):
    json_file = loop_through_links(url)
    data = pd.read_json(json_file)
    print(data)


if __name__ == '__main__':
    load_json("https://angel.co/companies?company_types[]=Startup&locations[]=1702-Toronto&stage[]=Series+C")
