from datetime import datetime, timedelta
import re

from configs import main_config
from scraper import scraper, get_urls_from_main_page
import sql
from args_parser import args_parse


TIME = 'time'
EVENT_KEY = 'event_key'
MAGNITUDE = 'magnitude'
LINK = 'link'
MAG_TEXT = 'mag_text'


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
    print(batch, duration, magnitude, attempts)
    event_keys = sql.select_events()
    event_list = get_urls_from_main_page(main_config.MAIN_URL, attempts)
    if not event_list:
        print('Could not connect at this time, try again later, or allow more tries')
        return

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
        return
    print(f'Added {len(scrape_urls)} new values to the database')
    list_of_dicts = scraper(attempts, scrape_urls)

    sql.create_db()
    sql.create_tables()
    sql.add_batch(list_of_dicts, batch)


if __name__ == '__main__':
    main()
