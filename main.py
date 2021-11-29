from datetime import datetime, timedelta
import re

from configs import main_config
from scraper import scraper, get_urls_from_main_page
import sql
from args_parser import args_parse


@args_parse
def main(batch, duration, magnitude, attempts):
    """

    :param batch:
    :param duration:
    :param magnitude:
    :param attempts:
    :return:
    """
    print(batch, duration, magnitude, attempts)
    event_keys = sql.select_events()
    event_list = get_urls_from_main_page(main_config.MAIN_URL, attempts)
    if not event_list:
        print('Could not connect at this time, try again later, or allow more tries')
        return
    for dic in event_list:
        time = datetime.fromisoformat(re.match('(.*)[(]', dic['time']).group(1).strip())
        event_key = re.match('.*/([a-z0-9]+)/$', dic['link']).group(1)
        mag = re.match('.*([0-9]+[.][0-9])+.*', dic['mag_text']).group(1)
        dic['time'] = time
        dic['event_key'] = event_key
        dic['magnitude'] = float(mag)

    scrape_urls = []
    for dic in event_list:
        if dic['event_key'] in event_keys:
            continue
        min_time = datetime.now() - timedelta(hours=duration)
        if dic['time'] >= min_time:
            if dic['magnitude'] >= magnitude:
                scrape_urls.append(dic['link'])

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
