import requests
import logging

import scraper_api_keys
from configs.api_config import *


def add_elevation(list_of_dicts):
    """
    adds elevation info from api to every event by location
    :param list_of_dicts: list of individual events to mutate
    """
    for dic in list_of_dicts:
        lat = dic['location_latitude']
        long = dic['location_longitude']
        json = requests.get(ELEVATION_URL.format(lat=lat, long=long)).json()
        elevation = json['results'][0]['elevation']
        dic['elevation'] = elevation
        logging.info(f'added elevation to event {dic["event_key"]}')
    return None


def get_weather_api(events):
    """
    creates a list of weather details for every event from api by location
    :param events: relevant event details for an api query
    :return: list of dictionaries of event weather details
    """
    keys = scraper_api_keys.stormglass_keys

    num_keys = len(keys)
    weather_events = []
    wasted_keys = False
    logging.info('started calling stormglass api, number of requests limited')

    for event in events:
        for i in range(num_keys):
            response = requests.get(WEATHER_URL,
                                    params={
                                        'lat': event['lat'],
                                        'lng': event['long'],
                                        'params': ','.join([TEMPERATURE, PRECIP, WIND]),
                                        'source': SOURCE,
                                        'start': event[TIME],
                                        'end': event[TIME] + HOUR
                                    }, headers={'Authorization': keys[i]}
                                    )
            json = response.json()
            if not json.get('hours'):
                if i == num_keys:
                    logging.warning('ran out lf requests allowed, please try again in 24 hours')
                    wasted_keys = True
                    break
                else:
                    logging.debug(f'key {i} is used up completely, moving to next key, number {i+1}')
                    continue
            logging.info(f'got weather information for event {event["id"]}')
            hours = json['hours']

            for hour in hours:
                weather_event = {'earthquake_event_id': event['id'],
                                 'time': hour[TIME],
                                 'air_temperature_deg_c': hour[TEMPERATURE][SOURCE],
                                 'precipitation_mm_h': hour[PRECIP][SOURCE],
                                 'wind_speed_m_s': hour[WIND][SOURCE]
                                 }
                weather_events.append(weather_event)
            break
        if wasted_keys:
            return weather_events
    return weather_events
