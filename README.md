# Web scraping project
The program retrieves available information from USGS Natrual Hazard website:

https://www.usgs.gov/natural-hazards

The website includes information on the latest earthquakes occurred in last 24 hours worldwide with magnitude above 2.5.
The program organizes the data in table format with relevant datatype.


## Web page for latest updates
https://earthquake.usgs.gov/earthquakes/map

## Web-driver 
The program uses Chrome driver that should be downloaded from website
[chrome driver ](https://chromedriver.chromium.org/downloads).
Relevant download should be performed according to your OS. 
You should check your Chrome version.

## Main program objective
The program scrapes from latest updates page urls for individual events (earthquakes).
Each url is scraped for relevant data. The data is parsed, inserted into table, cleaned and cast to relevant datatype.
The data is saved as output in pickle file which allows to preserve datatype.


## Main steps for scraping:
1. Get main page using selenium.
2. Select event elements.
3. Click programmatically on each event element.
4. Select pop-up element and get url text from each.
5. Modify url in order to get to origin/details page of each event. This page contains the relevant information.
6. Get each url page using selenium.
7. Select relevant information each page.
8. Parse received data and add into dictionary.
9. Convert list of dictionaries for all elements to pandas dataframe.
10. Process data and cast datatype when possible. 
11. Save into pickle (.pkl) file.

### Challenges
As the webpage is loading some elements are missing which caused us to get various errors.
To deal with this problem we used selenium package in order to wait for all elements to load properly and select them after they are in the DOM.
In addition, selenium was used in order to mimic human behaviour of clicking buttons.

```buildoutcfg
# Data scraping performed on Chrome browser.
driver = webdriver.Chrome()
driver.get(main_url)

# Selenium used for click, wait for page load and select relevant elements.
elements = driver.find_elements(By.TAG_NAME, 'mat-list-item')
driver.execute_script('arguments[0].click()', elements[1])
link = WebDriverWait(driver, timeout=3).until(lambda d: d.find_elements(By.CSS_SELECTOR, 'a.ng-tns-c101-0'))[-1]
```
