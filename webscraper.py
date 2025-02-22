from typing import List, Any

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json
import pandas as pd

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

url = 'https://vak.minobrnauki.gov.ru/adverts_list#tab=_tab:independent~'
driver.get(url)

wait = WebDriverWait(driver, 100)

date_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.col-md-2 > div > .input-group.date > input")))
print(date_element)
driver.execute_script("arguments[0].removeAttribute('readonly')", date_element)
date_element.clear()
date_element.send_keys("25.05.2007")

finish = False
df = pd.DataFrame()


def parse_page():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    adverts = []

    for link in soup.find_all('a', href=True):
        if 'advert_independent/' in link['href']:
            advert_url = link['href']
            adverts.append(advert_url)

    return adverts

all_adverts = []
count = 0
threshold = 10000000000


while True:
    if finish or count > threshold:
        break

    count += 1
    print(count)
    print(len(all_adverts))

    wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Следующая страница')]")))
    adverts = parse_page()
    all_adverts.extend(adverts)

    try:
        time.sleep(3)
        driver.find_element(By.XPATH, "//button[contains(text(), 'Следующая страница')]").click()
        time.sleep(3)

    except Exception as e:
        print('ERROR')
        print(repr(e))
        break

driver.quit()

print('DRIVER QUIT')
print(f'Total adverts found: {len(all_adverts)}')


with open('adverts.json', 'w', encoding='utf-8') as f:
    json.dump(list(all_adverts), f, ensure_ascii=False, indent=4)

print('PROCESS FINISHED')
