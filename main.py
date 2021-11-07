# import requests
# from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import re

driver = webdriver.Chrome()

# Navigate to
driver.get("https://earthquake.usgs.gov/earthquakes/map")

elements = driver.find_elements(By.TAG_NAME, 'mat-list-item')
driver.execute_script('arguments[0].click()', elements[1])
link = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.CSS_SELECTOR, 'a.ng-tns-c101-0'))[-1]
# sleep(3)

urls = []
for i in range(1, len(elements)):
    driver.execute_script('arguments[0].click()', elements[i])
    link = driver.find_elements(By.CSS_SELECTOR, 'a.ng-tns-c101-0')[0]
    urls.append(link.get_attribute('href'))

for i in range(len(urls)):
    if urls[i][-1] == '/':
        urls[i] = urls[i] + 'origin/detail'
    else:
        urls[i] = re.sub(r'/(\w*)$', '/origin/detail', urls[i])
urls = list(set(urls))
print(urls)

all_data = []
for url in urls:
    driver.get(url)

    # sleep(3)
    # elements = driver.find_elements(By.TAG_NAME, 'dt')
    elements = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.CSS_SELECTOR, 'dt'))
    for element in elements:
        print('text', element.text)
    data = driver.find_elements(By.TAG_NAME, 'dd')

    tuples = []
    for i in range(len(data)):
        tuples.append((elements[i].text, data[i].text.split('\n')))
    all_data.append(tuples)

# list_events = []
# for url in detail_urls:
#     driver.get(url)
#     elements = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.CSS_SELECTOR, 'dt'))
#     data = driver.find_elements(By.TAG_NAME, 'dd')
#     html = driver.page_source
#     soup = BeautifulSoup(html, 'lxml')
#     #Extracting into list data categories
#     clean_elem=[]
#     clean_elem.append('url') #first element will be url itself
#     elements = soup.find_all("dt")
#     for element in elements:
#         element = element.text.strip()
#         if 'uncertainty'in element:
#             element1 = element[:element.index("uncertainty")]
#             clean_elem.append(element1)
#             element2 = element1 + ' uncertainty'
#             clean_elem.append(element2)
#         else:
#             clean_elem.append(element)
#     #Extracting into list data itself
#     clean_data=[]
#     clean_data.append(url) #first element will be url itself
#     data = soup.find_all("dd")
#     for info in data:
#         info = info.text.strip()
#         if '±' in info:
#             info1 = info[:info.index('±')].strip()
#             clean_data.append(info1)
#             info_uncert = info[info.index('±'):].strip()
#             clean_data.append(info_uncert)
#         else:
#             clean_data.append(info)
#     #Pairing categories with data itself
#     data_extract = dict(list(zip(clean_elem, clean_data)))
#     list_events.append(data_extract)
#     print(f'Status: events from url {url} added to dict')
# return pd.DataFrame(list_events)
for line in all_data:
    print(line)

