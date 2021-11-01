import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()

# Navigate to
driver.get("https://earthquake.usgs.gov/earthquakes/map")

elements = driver.find_elements(By.TAG_NAME, 'mat-list-item')
driver.execute_script('arguments[0].click()', elements[0])
sleep(3)

urls = []
for i in range(1, len(elements)):
    driver.execute_script('arguments[0].click()', elements[i])
    sleep(0.2)
    link = driver.find_elements(By.TAG_NAME, 'a')[-1]
    urls.append(link.get_attribute('href'))

for i in range(len(urls)):
    if urls[i][-1] == '/':
        urls[i] = urls[i] + 'origin/detail'
    else:
        urls[i] = urls[i][:-4] + 'origin/detail'
urls = list(set(urls))
print(urls)

all_data = []
for url in urls:
    driver.get(url)
    sleep(3)
    elements = driver.find_elements(By.TAG_NAME, 'dt')
    data = driver.find_elements(By.TAG_NAME, 'dd')

    tuples = []
    for i in range(len(data)):
        tuples.append((elements[i].text, data[i].text.split('\n')))
    all_data.append(tuples)

for line in all_data:
    print(line)

