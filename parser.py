# Значения ряда атрибутов заменены на Placeholders

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import json

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(options=options)

output_csv = 'database.csv'
base_url = 'BASE_URL'

combined_file_path = "adverts.json"
with open(combined_file_path, 'r', encoding='utf-8') as file:
    all_adverts = json.load(file)

data_list = []


def parse_advert(url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ELEMENT")))

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    table = soup.find('table', class_='CLASS')

    data = {'URL': url, 'Самостоятельное присуждение': 1}

    if table:
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) == 2:
                key = cells[0].get_text(strip=True)
                value = cells[1].get_text(strip=True)
                if key == "Номер и дата редакции объявления":
                    value = value.replace('\t', '').strip()
                data[key] = value

                if key == "Автореферат":
                    pdf_link = base_url + cells[1].find('a')['href']
                    data['PDF Link'] = pdf_link

    return data

finish = False
count = 0

for advert in all_adverts:
    print(count)
    count += 1
    if finish:
        break
    full_url = base_url + advert
    advert_data = parse_advert(full_url)
    data_list.append(advert_data)

driver.quit()

df = pd.DataFrame(data_list)
df.to_csv(output_csv, index=False)


print('PROCESS FINISHED')
