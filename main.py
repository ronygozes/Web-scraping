"""
The program retrieves available information from website:
https://www.usgs.gov/natural-hazards/earthquake-hazards/earthquakes
that includes information on the latest earthquakes occurred in last 24 hours worldwide with magnitude above 2.5.
The program organizes the data in table format with relevant datatype.
Please read README.md document for more details.
"""

import selenium.common.exceptions as exc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import re
from time import sleep

MAIN_URL = "https://earthquake.usgs.gov/earthquakes/map"
NUM_TRIES = 50
# Data scraping performed on Chrome browser.


def get_urls_from_main_page(main_url, driver):
    """ The function receives as parameter url to webpage of earthquake updates and
    returns list of urls of individual events.
    """
    driver.get(main_url)
    elements = driver.find_elements(By.TAG_NAME, 'mat-list-item')
    driver.execute_script('arguments[0].click()', elements[1])
    link = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.CSS_SELECTOR, 'a.ng-tns-c101-0'))[-1]

    urls = []
    # Collection of urls to individual events
    for i in range(1, len(elements)):
        driver.execute_script('arguments[0].click()', elements[i])
        link = driver.find_elements(By.CSS_SELECTOR, 'a.ng-tns-c101-0')[0]
        urls.append(link.get_attribute('href'))
    return urls


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
    """
    list_events = []
    for url in detail_urls:
        driver.get(url)
        elements = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.CSS_SELECTOR, 'dt'))
        sleep(0.1)
        data = driver.find_elements(By.TAG_NAME, 'dd')

        # Extracting into list data categories, first element is url
        clean_elem = ['url']
        for element in elements:
            element = element.text
            if 'uncertainty' in element:
                element1 = element[:element.index("uncertainty") - 1]
                clean_elem.append(element1)
                element2 = element1.split()[0] + ' uncertainty'
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
                info_uncert = info[info.index('±')+1:].strip()
                clean_data.append(info_uncert)
            else:
                clean_data.append(info)

            # Pairing categories with data itself
        data_extract = dict(list(zip(clean_elem, clean_data)))
        list_events.append(data_extract)
        print(f'Status: events from url {url} added to dict')

    return pd.DataFrame(list_events)


def clean_dataframe(event_dataframe):
    """"
    The function performs manual cleaning of labels, update of column names, removal of units from values
    and moving the units to column names, assigning datatype to numerical columns.
    The function returns new dataframe.
    """
    # Rename of columns to include units
    df_event_mod = event_dataframe.rename(columns={'Location uncertainty': 'Location uncertainty (km)',
                                                   'Depth': 'Depth (km)',
                                                   'Depth uncertainty': 'Depth uncertainty (km)',
                                                   'Minimum Distance': 'Minimum Distance (km)',
                                                   'Travel Time Residual': 'Travel Time Residual (s)',
                                                   'Azimuthal Gap': 'Azimuthal Gap (deg)'})

    # Remove common units and strings from numeric
    df_event_mod['Location uncertainty (km)'] = df_event_mod['Location uncertainty (km)'].str.replace(' km', '')
    df_event_mod['Depth (km)'] = df_event_mod['Depth (km)'].str.replace(' km', '')
    df_event_mod['Travel Time Residual (s)'] = df_event_mod['Travel Time Residual (s)'].str.replace(' s', '')
    df_event_mod['Azimuthal Gap (deg)'] = df_event_mod['Azimuthal Gap (deg)'].str.replace('°', '')
    df_event_mod['Minimum Distance (km)'] = df_event_mod['Minimum Distance (km)'].str.replace(' km', '')

    # Convert columns from strings to relevant datatype
    df_event_mod['Magnitude uncertainty'] = df_event_mod['Magnitude uncertainty'].astype('float')
    df_event_mod['Location uncertainty (km)'] = df_event_mod['Location uncertainty (km)'].astype('float')
    df_event_mod['Depth (km)'] = round(pd.to_numeric(df_event_mod['Depth (km)'], errors='coerce'), 3)
    df_event_mod['Depth uncertainty (km)'] = round(pd.to_numeric(df_event_mod['Depth uncertainty (km)'], errors='coerce'), 3)
    df_event_mod['Travel Time Residual (s)'] = pd.to_numeric(df_event_mod['Travel Time Residual (s)'], errors='coerce')
    df_event_mod['Number of Stations'] = pd.to_numeric(df_event_mod['Number of Stations'], errors='coerce')
    df_event_mod['Origin Time'] = pd.to_datetime(df_event_mod['Origin Time'])
    df_event_mod['Azimuthal Gap (deg)'] = pd.to_numeric(df_event_mod['Azimuthal Gap (deg)'], errors='coerce')
    df_event_mod['Number of Stations'] = pd.to_numeric(df_event_mod['Number of Stations'], downcast='integer',
                                                       errors='coerce')
    df_event_mod['Number of Phases'] = pd.to_numeric(df_event_mod['Number of Phases'], downcast='integer',
                                                     errors='coerce')
    return df_event_mod


def main():
    for i in range(NUM_TRIES):
        try:
            driver = webdriver.Chrome()
            new_url_list = list(set(get_urls_from_main_page(MAIN_URL, driver)))
            url_list = []
            with open('urls.txt', 'a+') as file:
                file.seek(0)
                old_url_list = [line.strip() for line in file.readlines()]
                for j, url in enumerate(new_url_list):
                    if url not in old_url_list:
                        print(j, url)
                        url_list.append(url)
                        file.write(url + '\n')
            if url_list:
                detail_url = get_event_url(url_list)
                dataframe = get_event_details(detail_url, driver)
                updated_df = clean_dataframe(dataframe)
                updated_df.to_csv('df.csv')
                updated_df.to_pickle('earthquakes.pkl')  # saving in pickle format to preserve datatype.
        except exc.TimeoutException as e:
            print(f'Timeout {e}')
        except exc.StaleElementReferenceException as e:
            print(f'Stale {e}')
        except exc.InvalidSessionIdException as e:
            print(f'ID {e}')
        except FileNotFoundError:
            with open('urls.txt', 'w') as file:
                file.write('')
        else:
            break
        finally:
            driver.close()


if __name__ == '__main__':
    main()
