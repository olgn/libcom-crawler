# This script crawls all libcom reading lists and downloads all of the
# related pdf content. This can then be translated into epub documents for e-readers.

import os
from tqdm import tqdm
import requests
from urllib.parse import unquote
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


target_reading_list = 'https://libcom.org/library/libcomorg-reading-guide'

chrome_options = Options()
# chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chromedriver_path = '/usr/local/bin/chromedriver'
browser = webdriver.Chrome(chromedriver_path, chrome_options=chrome_options)

browser.get(target_reading_list)


text_path = './texts'

try:
    os.makedirs(text_path)
except:
    print('text directory already exists')

reading_list = browser.find_element_by_xpath('//*[@id="book-navigation-43969"]/ul')
reading_lists = reading_list.find_elements_by_tag_name('a')

reading_list_urls = {}
for reading_list in reading_lists:
    reading_list_name = reading_list.text
    reading_list_link = reading_list.get_attribute('href')
    reading_list_urls[reading_list_name] = reading_list_link

for reading_list in reading_list_urls.keys():
    print('crawling link text for reading list:', reading_list)
    reading_list_link = reading_list_urls[reading_list]
    browser.get(reading_list_link)
    links = browser.find_elements_by_xpath('//*[@id="node-page"]/ul/li/a')
    target_links = []
    for link in links:
        location = link.get_attribute('href')
        if ('libcom' in location and 'tags' not in location):
            target_links.append(location)

    target_downloads = []
    for target in target_links:
        browser.get(target)
        try:
            upload_field = browser.find_element_by_id('node-sidebar')
            upload_items = upload_field.find_elements_by_partial_link_text('.pdf')
            for upload_item in upload_items:
                target_downloads.append(upload_item.get_attribute('href'))
        except NoSuchElementException:
            print('no sidebar present')

    print('downloading reading list:', reading_list)
    reading_list_path = os.path.join(text_path, reading_list)
    try:
        os.makedirs(reading_list_path)
    except:
        print('directory already exists')
    for target in tqdm(target_downloads):
        r = requests.get(target)
        target_name = unquote(target.split('/')[-1])
        open(os.path.join(reading_list_path, target_name), 'wb').write(r.content)


browser.quit()
    

print('crawling complete.')