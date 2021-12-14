import pymysql.cursors
from datetime import datetime, timedelta, timezone

import personal
from configs import sql_config

PASSWORD = personal.PASSWORD
USER = personal.USER


def create_db():
    """
    The function creates new sql database if it does not exist yet.
    It takes as constant user name and password from "personal" config file.
    """
    with pymysql.connect(host=sql_config.HOST, user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.CREATE_DATABASE)


def create_tables():
    """
    The function creates new sql tables if they do not exist yet.
    It takes as constant user name and password from "personal" config file.
    """
    with pymysql.connect(host=sql_config.HOST, user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.USE)
            cursor.execute(sql_config.CREATE_REVIEW)
            cursor.execute(sql_config.CREATE_CONTRIBUTOR)
            cursor.execute(sql_config.CREATE_FE_REGION)
            cursor.execute(sql_config.CREATE_CATALOG)
            cursor.execute(sql_config.CREATE_EARTHQUAKES)
            cursor.execute(sql_config.CREATE_WEATHER)


def add_review_status(cursor, dic):
    """
    Addition of line to review_status table after check that does not exist
    and updates the dictionary of event with review_id instead of review status.

    :param cursor: pymysql object that allows access to sql
    :param dic: dictionary of earthquake event details
    """
    sql = sql_config.INSERT_STR.format(table='review_status', column='review_status', value=dic['review_status'])
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='review_status', field='review_status', value=dic['review_status'])
    cursor.execute(sql2)
    line_id = cursor.fetchone()[0]
    del dic['review_status']
    dic['review_status_id'] = line_id


def add_fe_region(cursor, dic):
    """
    Adds a line to fe_region table after check that does not exist
    and updates the dictionary of event with fe_region_id instead of fe_region.

    :param cursor: pymysql object that allows access to sql
    :param dic: dictionary of earthquake event details
    """
    sql = sql_config.INSERT_STR.format(table='fe_region', column='fe_region', value=dic['fe_region'])
    #todo add logging
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='fe_region', field='fe_region', value=dic['fe_region'])
    cursor.execute(sql2)
    line_id = cursor.fetchone()[0]
    del dic['fe_region']
    dic['fe_region_id'] = line_id


def add_catalog(cursor, dic):
    """
    Adds a line to catalog table after check that does not exist
    and updates the dictionary of event with catalog_id instead of catalog.

    :param cursor: pymysql object that allows access to sql
    :param dic: dictionary of earthquake event details
    """
    sql = sql_config.INSERT_STR.format(table='catalog', column='catalog', value=dic['catalog'])
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='catalog', field='catalog', value=dic['catalog'])
    cursor.execute(sql2)
    line_id = cursor.fetchone()[0]
    del dic['catalog']
    dic['catalog_id'] = line_id


def add_contributor(cursor, dic):
    """
    Adds a line to contributor table after check that does not exist
    and updates the dictionary of event with contributor_id instead of contributor field.

    :param cursor: pymysql object that allows access to sql
    :param dic: dictionary of earthquake event details
    """
    sql = sql_config.INSERT_STR.format(table='contributor', column='contributor', value=dic['contributor'])
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='contributor', field='contributor', value=dic['contributor'])
    cursor.execute(sql2)
    line_id = cursor.fetchone()[0]
    del dic['contributor']
    dic['contributor_id'] = line_id


def add_earthquake_event(cursor, dic):
    """
    It is assumed that the dictionary already contains foreign ids for other related tables.
    Adds a line to main earthquakes table after check that does not exist.

    :param cursor: pymysql object that allows access to sql
    :param dic: dictionary of earthquake event details
    """
    #todo add logging('add_earthquake_event')
    values = ["'" + str(value) + "'" for value in dic.values()]
    #todo add logging('sql add earth', values)
    values[0] = values[0][1:]
    values[-1] = values[-1][:-1]
    sql = sql_config.INSERT_STR.format(table='earthquake_events', column=', '.join(dic.keys()), value=", ".join(values))
    cursor.execute(sql)


def add_weather_events(weather_events, batch_size):
    """
    adds weather events to the database in its own table
    :param weather_events: list of weather events details
    :param batch_size: integer - define how many lines to add before committing to the database
    """
    with pymysql.connect(host=sql_config.HOST, user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.USE)
            for i, dic in enumerate(weather_events):
                if i % batch_size == 0:
                    connection.commit()

                values = ["'" + str(value) + "'" for value in dic.values()]
                #todo add logging('sql add weather', values)
                values[0] = values[0][1:]
                values[-1] = values[-1][:-1]
                sql = sql_config.INSERT_STR.format(table='weather', column=', '.join(dic.keys()),
                                                   value=", ".join(values))
                cursor.execute(sql)

            connection.commit()


def add_batch(dicts, batch_size):
    """
    The function checks that there are no duplicate lines in scrapped data.
    The function calls other functions to add data to SQL tables
    and performs a commit according to defined batch size.
    It takes as constant user name and password from "personal" config file.

    :param dicts: list of dictionaries (event details)
    :param batch_size: integer - define how many lines to add before committing to the database
    """
    with pymysql.connect(host=sql_config.HOST, user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.USE)

            new_dicts = []
            keys = []
            for dic in dicts:
                if dic['event_key'] not in keys:
                    new_dicts.append(dic)
                    keys.append(dic['event_key'])

            for i, dic in enumerate(new_dicts):
                if i % batch_size == 0:
                    connection.commit()

                add_review_status(cursor, dic)
                add_fe_region(cursor, dic)
                add_catalog(cursor, dic)
                add_contributor(cursor, dic)
                add_earthquake_event(cursor, dic)

            connection.commit()


def select_events():
    """
    The function queries sql database for event_key (unique identifier) from last TIME_DELTA days.
    It takes as constant user name and password from "personal" config file.
    :return: a list of event_keys.
    """
    with pymysql.connect(host=sql_config.HOST, user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.USE)
            time = datetime.now() - timedelta(days=sql_config.TIME_DELTA)
            sql = sql_config.SELECT_EVENT_KEY_BY_TIME.format(time=time)
            cursor.execute(sql)
            return [x[0] for x in cursor.fetchall()]


def get_details_by_key(key):
    """
    get details about a specific event by event key from earthquake_events table in database
    :param key: event key to retrieve
    :return: dictionary with event details
    """
    with pymysql.connect(host=sql_config.HOST, user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.USE)
            sql = f'SELECT id, origin_time, location_latitude, location_longitude FROM earthquake_events ' \
                  f'WHERE event_key="{key}"'
            cursor.execute(sql)
            event = cursor.fetchone()

            return {'id': event[0], 'time': event[1].timestamp(),
                    'lat': event[2], 'long': event[3]}




