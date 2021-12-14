from datetime import datetime, timedelta
import re

from configs.main_config import *
from scraper import scraper, get_urls_from_main_page
import sql
from args_parser import args_parse
import api
import logging

logging.basicConfig(filename=f'./logging/main_log_{datetime.now().date()}.log',
                    format='%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s',
                    level=logging.INFO)


@args_parse
def main(batch, duration, magnitude, attempts):
    """
    this function receives a few parameters, and scrapes earthquake data accordingly.
    It then calls sql utility function to insert the results into the database
    :param batch: batch size to commit in the database
    :param duration: how long back to scrape for values, 1-24 hours
    :param magnitude: threshold magnitude for earthquake to scrape
    :param attempts: number of attempts to try and scrape the site before giving up
    """
    logging.info('started program')
    sql.create_db()
    sql.create_tables()
    logging.info('database connection working')
    event_keys = sql.select_events()
    event_list = get_urls_from_main_page(MAIN_URL, attempts)
    if not event_list:
        print('Could not connect at this time, try again later, or allow more tries')
        logging.critical('Could not connect at this time, try again later, or allow more tries')
        return None
    logging.info('got urls for scraping')

    for dic in event_list:
        time = datetime.fromisoformat(re.match('(.*)[(]', dic[TIME]).group(1).strip())
        event_key = re.match('.*/([a-z0-9]+)/$', dic[LINK]).group(1)
        mag = re.match('.*([0-9]+[.][0-9])+.*', dic[MAG_TEXT]).group(1)
        dic[TIME] = time
        dic[EVENT_KEY] = event_key
        dic[MAGNITUDE] = float(mag)

    scrape_urls = []
    for dic in event_list:
        if dic[EVENT_KEY] in event_keys:
            continue
        min_time = datetime.now() - timedelta(hours=duration)
        if dic[TIME] >= min_time:
            if dic[MAGNITUDE] >= magnitude:
                scrape_urls.append(dic[LINK])

    if not scrape_urls:
        print('No new values available at this time, try again later')
        logging.info('No new values available at this time')
        return None

    list_of_dicts = scraper(attempts, scrape_urls)

    api.add_elevation(list_of_dicts)
    logging.info('added elevation to events')

    sql.add_batch(list_of_dicts, batch)
    print(f'Added {len(list_of_dicts)} earthquake events')
    logging.info(f'Added {len(list_of_dicts)} earthquake events')

    keys = [dic[EVENT_KEY] for dic in list_of_dicts]
    events = []
    for key in keys:
        events.append(sql.get_details_by_key(key))

    weather_events = api.get_weather_api(events)
    if not weather_events:
        print('Weather keys are out of tries')
        logging.warning('Weather keys are out of tries, limited number of requests for each key,'
                        ' Keys available within 24 hours of use')
        return None

    sql.add_weather_events(weather_events, batch)
    print(f'Added {len(weather_events)} weather events')
    return None


if __name__ == '__main__':
    main()
