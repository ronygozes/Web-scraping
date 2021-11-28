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
        sleep(0.5)
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
        print(f'Status: events from url {url} added to dict')

    return pd.DataFrame(list_events)


def split_magnitude(df):
    """
    The function receives a dataframe as an argument,
    performs split of column magnitude to two separate columns - value and units.
    The function returns new dataframe.
    """
    df[['magnitude', 'magnitude_units']] = df['Magnitude'].str.split(' ', expand=True)
    df = df.drop('Magnitude', axis=1)

    return df


def rename_column(event_dataframe):
    """
    The function receives a dataframe as an argument,
    performs manual update of column names to fit column names in sql main table 'earthquakes_events'.
    The new names include also units where possible to remove units from the values
    The function returns new dataframe.
    """
    df_event_mod = event_dataframe.rename(columns={'Magnitude_uncertainty': 'magnitude_uncertainty',
                                                   'Location': 'location',
                                                   'Location_uncertainty': 'location_uncertainty_km',
                                                   'Depth': 'depth_km',
                                                   'Depth_uncertainty': 'depth_uncertainty_km',
                                                   'Origin Time': 'origin_time',
                                                   'Number of Stations': 'num_of_stations',
                                                   'Number of Phases': 'num_of_phases',
                                                   'Minimum Distance': 'minimum_distance_km',
                                                   'Travel Time Residual': 'travel_time_residual_sec',
                                                   'Azimuthal Gap': 'azimuthal_gap_deg',
                                                   'FE Region': 'fe_region',
                                                   'Review Status': 'review_status',
                                                   'Catalog': 'catalog',
                                                   'Contributor': 'contributor'})

    return df_event_mod


def remove_units_from_values(df_event_mod):
    """
    The function receive dataframe as argument and performs removal of units from values.
    The function returns updated dataframe.
    """
    df_event_mod['location_uncertainty_km'] = df_event_mod['location_uncertainty_km'].str.replace(' km', '')
    df_event_mod['depth_km'] = df_event_mod['depth_km'].str.replace(' km', '')
    df_event_mod['travel_time_residual_sec'] = df_event_mod['travel_time_residual_sec'].str.replace(' s', '')
    df_event_mod['azimuthal_gap_deg'] = df_event_mod['azimuthal_gap_deg'].str.replace('°', '')
    df_event_mod['minimum_distance_km'] = df_event_mod['minimum_distance_km'].str.replace(' km', '').str.replace(
        ' \(.+\)', '')
    df_event_mod = df_event_mod.drop(['url', 'Location Source', 'Magnitude Source'], axis=1)
    df_event_mod['contributor'] = df_event_mod['contributor'].str.replace(' 1', '')
    df_event_mod['event_key'] = df_event_mod['catalog'].str.split(' ').str[2]
    df_event_mod['catalog'] = df_event_mod['catalog'].str.split(' ').str[0]
    cols = df_event_mod.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df_event_mod = df_event_mod[cols]

    return df_event_mod


def convert_datatype(df_event_mod):
    """
    The function receive dataframe as argument and assigns datatype to numerical columns.
    The function returns updated dataframe.
    """
    df_event_mod['magnitude'] = df_event_mod['magnitude'].astype('float')
    df_event_mod['magnitude_uncertainty'] = df_event_mod['magnitude_uncertainty'].astype('float')
    df_event_mod['location_uncertainty_km'] = df_event_mod['location_uncertainty_km'].astype('float')
    df_event_mod['depth_km'] = round(pd.to_numeric(df_event_mod['depth_km'], errors='coerce'), 3)
    df_event_mod['depth_uncertainty_km'] = round(pd.to_numeric(df_event_mod['depth_uncertainty_km'], errors='coerce'),
                                                 3)
    df_event_mod['travel_time_residual_sec'] = pd.to_numeric(df_event_mod['travel_time_residual_sec'], errors='coerce')
    df_event_mod['num_of_stations'] = pd.to_numeric(df_event_mod['num_of_stations'], downcast='integer',
                                                    errors='coerce')
    df_event_mod['origin_time'] = pd.to_datetime(df_event_mod['origin_time'])
    df_event_mod['azimuthal_gap_deg'] = pd.to_numeric(df_event_mod['azimuthal_gap_deg'], errors='coerce')
    df_event_mod['num_of_phases'] = pd.to_numeric(df_event_mod['num_of_phases'], downcast='integer',
                                                  errors='coerce')

    return df_event_mod


def clean_dataframe(dataframe):
    """
    The function receives dataframe as argument and calls different function to perform data cleaning and labeling.
    The function returns new dataframe.
    """
    event_dataframe = split_magnitude(dataframe)
    updated_df = rename_column(event_dataframe)
    updated_df1 = remove_units_from_values(updated_df)
    df_event_mod = convert_datatype(updated_df1)

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
                updated_df.to_csv('for_test.csv', index=False)
                list_of_dicts = updated_df.to_dict(orient='records')
                print(f'Created list of dictionaries with {len(list_of_dicts)} events.')
                return list_of_dicts

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
