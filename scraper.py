"""
The program retrieves available information from website:
https://www.usgs.gov/natural-hazards/earthquake-hazards/earthquakes
that includes information on the latest earthquakes occurred in last 24 hours worldwide with magnitude above 2.5.
The program organizes the data in table format with relevant datatype.
Please read README.md document for more details.
Data scraping performed on Chrome browser.
"""
import selenium.common.exceptions as exc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import re
from time import sleep
import logging

from configs.scraper_config import *
from clean_data import clean_dataframe


def get_urls_from_main_page(main_url, attempts):
    """ The function receives as parameter url to webpage of earthquake updates and
    returns list of urls of individual events.
    """
    for _ in range(attempts):
        driver = webdriver.Chrome()
        logging.info('connected to web driver')
        try:
            driver.get(main_url)
            elements = driver.find_elements(By.TAG_NAME, ELEMENTS_CLASS)

            driver.execute_script(JS_CLICK, elements[1])
            WebDriverWait(driver, timeout=MAX_SLEEP).until(lambda d: d.find_elements(
                By.CSS_SELECTOR, LINK_ELEMENT_CLASS))[-1]
            urls = []

            # Collection of urls of individual events
            for i in range(1, len(elements)):
                driver.execute_script(JS_CLICK, elements[i])
                link_element = driver.find_elements(By.CSS_SELECTOR, LINK_ELEMENT_CLASS)
                link_element = link_element[0]
                link = link_element.get_attribute('href')
                mag_text = link_element.get_attribute('text')
                time_element = driver.find_elements(By.CSS_SELECTOR, TIME_ELEMENT_CLASS)[0]
                time = time_element.get_attribute('innerText')
                dic = {LINK: link, MAG_TEXT: mag_text, TIME: time}
                urls.append(dic)
        except exc.TimeoutException as e:
            logging.error(f'Timeout {e}')
        except exc.StaleElementReferenceException as e:
            logging.error(f'Stale {e}')
        except exc.InvalidSessionIdException as e:
            logging.error(f'ID {e}')
        except Exception as e:
            logging.error('Error not recognized')
        else:
            logging.info('got urls for scraping')
            return urls
        finally:
            driver.close()


def get_event_url(urls):
    """ preparing urls with relevant information for "details page"
    parameters: list of urls
    returns: updated list of urls for individual page
    """
    new_url_list = []
    for url in urls:
        if url[-1] == '/':
            url = url + 'origin/detail'
            new_url_list.append(url)
        else:
            url = re.sub(r'/(\w*)$', '/origin/detail', url)
            new_url_list.append(url)

    detail_urls = list(set(new_url_list))
    return detail_urls


def get_event_details(detail_urls, driver):
    """
    The function receives list of urls providing details for specific earthquakes.
    After extraction relevant information it returns a dataframe table
    where each row includes information on individual earthquake.
    :param detail_urls: list of events urls
    :param driver: webchrome driver
    :return: dataframe with events details
    """
    list_events = []
    for url in detail_urls:
        driver.get(url)
        elements = WebDriverWait(driver, timeout=MAX_SLEEP).until(lambda d: d.find_elements(
            By.CSS_SELECTOR, 'dt'))
        sleep(SLEEP)

        data = driver.find_elements(By.TAG_NAME, 'dd')

        # Extracting into list data categories, first element is url
        clean_elem = ['url']
        for element in elements:
            element = element.text
            if 'uncertainty' in element:
                element1 = element[:element.index("uncertainty") - 1]
                clean_elem.append(element1)
                element2 = element1.split()[0] + '_uncertainty'
                clean_elem.append(element2)
            else:
                clean_elem.append(element)

        # Extracting into list data itself, first element is url
        clean_data = [url]
        for info in data:
            info = info.text
            if '±' in info:
                info1 = info[:info.index('±')].strip()
                clean_data.append(info1)
                info_uncert = info[info.index('±') + 1:].strip()
                clean_data.append(info_uncert)
            else:
                clean_data.append(info)

        # Pairing categories with data itself
        data_extract = dict(list(zip(clean_elem, clean_data)))
        list_events.append(data_extract)

    return pd.DataFrame(list_events)


def scraper(attempts, url_list):
    """
    scrapes for earthquake events from usgs website
    :param attempts: num of scrape attempts before giving up
    :param url_list: a list of urls which contain earthquake data to scrape
    :return: a list of dictionaries with each one containing all relevant data from one url
    """
    for _ in range(attempts):
        driver = webdriver.Chrome()
        try:
            detail_url = get_event_url(url_list)
            logging.info('url list created')
            dataframe = get_event_details(detail_url, driver)
            logging.info('got event details and converted to dataframe')
            updated_df = clean_dataframe(dataframe)
            logging.info('cleaned data and removed units from dataframe')
            list_of_dicts = updated_df.to_dict(orient='records')
        except exc.TimeoutException as e:
            logging.error(f'Timeout {e}')
        except exc.StaleElementReferenceException as e:
            logging.error(f'Stale {e}')
        except exc.InvalidSessionIdException as e:
            logging.error(f'ID {e}')
        except Exception as e:
            logging.error('Error not recognized')
        else:
            logging.info(f'Created list of dictionaries with {len(list_of_dicts)} events.')
            return list_of_dicts
        finally:
            driver.close()
