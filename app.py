# Dependencies to install:
#
# Chrome driver for selenium
# https://tecadmin.net/setup-selenium-chromedriver-on-ubuntu/
#
#
# apt install chromium-chromedriver
#
# Selenium
# python3 -m pip install selenium
#
# Open Py XL
# python3 -m pip install openpyxl
#
# Pandas
# python3 -m pip install pandas
#
# ------------------------------------------------------------------------

from selenium import webdriver
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import pandas as pd
import os

import time

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('chromedriver', options=chrome_options)


def readTableHead(table):
    titles = []
    head_rows = table.find_elements(
        By.XPATH, "//thead[@id='mainForm:dataTable_head']/tr")

    columns = head_rows[0].find_elements(By.TAG_NAME, 'th')
    for column in columns:
        titles.append(column.text)

    return titles


def readTableBody(table, thead_titles, lines=[]):
    table_rows = table.find_elements(
        By.XPATH, "//tbody[@id='mainForm:dataTable_data']/tr")

    row_counter = 0
    for row in table_rows:
        item = {}

        row_columns = row.find_elements(By.TAG_NAME, 'td')

        columns_counter = 0
        for column in row_columns:
            item[thead_titles[columns_counter]] = column.text
            columns_counter = columns_counter+1

        lines.append(item)
        row_counter = row_counter+1

    return lines


def readPagination():
    paginate_info = driver.find_element(
        By.CSS_SELECTOR, 'div.pagination-wrapper p')
    parts = paginate_info.text.split('PAGE ')[1].split(' / ')
    return {'total_page': int(parts[1]), 'current_page': int(parts[0])}


def exportResult(result):
    columns = result[0].keys()

    data_frame = pd.DataFrame(result, columns=columns)

    path = os.getcwd()

    data_frame.to_excel(path+'/excel.xlsx', index=False, header=True)

    print('File!')
    print(path+'/excel.xlsx')


def readPageTable(lines, iteration):
    table = driver.find_element(
        By.CSS_SELECTOR, 'table.results.overview-result')

    thead_titles = readTableHead(table)

    pagination = readPagination()
    print('Paginate: ', pagination)

    lines = readTableBody(table, thead_titles, lines)

    print('Finish read table ', pagination['current_page'])

    if (pagination['current_page'] < 2):
        WebDriverWait(driver, 60).until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, 'ul.pagination.pagination-sm li')))

        pagination_buttons = driver.find_elements(
            By.CSS_SELECTOR, 'ul.pagination.pagination-sm li')

        button_nextpage = pagination_buttons[len(
            pagination_buttons)-2].find_element(By.CSS_SELECTOR, 'a')

        driver.execute_script("arguments[0].click();", button_nextpage)

        print('Wating for Page update...')

        current_page = pagination['current_page']
        while current_page < (pagination['current_page'] + 1):
            time.sleep(5)
            pagination_check = readPagination()
            current_page = pagination_check['current_page']

        print('time to read next table')
        iteration = iteration+1
        return readPageTable(lines, iteration)
    else:
        return lines


print(':: Starting the mission ::')

url = 'https://www.sportstats.ca/display-results.xhtml?raceid=114430'
driver.get(url)
print('Opened URL: ', url)

result = readPageTable([], 1)
print('Lines registered: ', len(result))
exportResult(result)


print(':: Mission Finished ::')
