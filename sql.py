import pymysql.cursors
import personal

from configs import sql_config
from datetime import datetime, timedelta


PASSWORD = personal.PASSWORD
USER = personal.USER


def create_db():
    """

    :return:
    """
    with pymysql.connect(host='localhost', user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.CREATE_DATABASE)


def create_tables():
    """

    :return:
    """
    with pymysql.connect(host='localhost', user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.USE)
            cursor.execute(sql_config.CREATE_REVIEW)
            cursor.execute(sql_config.CREATE_CONTRIBUTOR)
            cursor.execute(sql_config.CREATE_FE_REGION)
            cursor.execute(sql_config.CREATE_CATALOG)
            cursor.execute(sql_config.CREATE_EARTHQUAKES)


def add_review_status(cursor, dic):
    """

    :param cursor:
    :param dic:
    :return:
    """
    sql = sql_config.INSERT_STR.format(table='review_status', column='review_status', value=dic['review_status'])
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='review_status', field='review_status', value=dic['review_status'])
    cursor.execute(sql2)
    id = cursor.fetchone()[0]
    del dic['review_status']
    dic['review_status_id'] = id


def add_fe_region(cursor, dic):
    """

    :param cursor:
    :param dic:
    :return:
    """
    sql = sql_config.INSERT_STR.format(table='fe_region', column='fe_region', value=dic['fe_region'])
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='fe_region', field='fe_region', value=dic['fe_region'])
    cursor.execute(sql2)
    id = cursor.fetchone()[0]
    del dic['fe_region']
    dic['fe_region_id'] = id


def add_catalog(cursor, dic):
    """

    :param cursor:
    :param dic:
    :return:
    """
    sql = sql_config.INSERT_STR.format(table='catalog', column='catalog', value=dic['catalog'])
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='catalog', field='catalog', value=dic['catalog'])
    cursor.execute(sql2)
    id = cursor.fetchone()[0]
    del dic['catalog']
    dic['catalog_id'] = id


def add_contributor(cursor, dic):
    """

    :param cursor:
    :param dic:
    :return:
    """
    sql = sql_config.INSERT_STR.format(table='contributor', column='contributor', value=dic['contributor'])
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='contributor', field='contributor', value=dic['contributor'])
    cursor.execute(sql2)
    id = cursor.fetchone()[0]
    del dic['contributor']
    dic['contributor_id'] = id


def add_earthquake_event(cursor, dic):
    """

    :param cursor:
    :param dic:
    :return:
    """
    values = ["'" + str(value) + "'" for value in dic.values()]
    values[0] = values[0][1:]
    values[-1] = values[-1][:-1]
    sql = sql_config.INSERT_STR.format(table='earthquake_events', column=', '.join(dic.keys()), value=", ".join(values))
    cursor.execute(sql)


def add_batch(dicts, batch_size):
    """

    :param dicts:
    :param batch_size:
    :return:
    """
    with pymysql.connect(host='localhost', user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.USE)

            new_dicts = []
            keys = []
            for dic in dicts:
                if dic['event_key'] not in keys:
                    new_dicts.append(dic)
                    keys.append(dic['event_key'])

            sql = "SELECT event_key FROM earthquake_events"
            cursor.execute(sql)
            events_keys = [key[0] for key in cursor.fetchall()]

            for i, dic in enumerate(new_dicts):
                if dic['event_key'] in events_keys:
                    continue
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

    :return:
    """
    with pymysql.connect(host='localhost', user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.USE)
            time = datetime.now() - timedelta(days=2)
            sql = f'SELECT event_key FROM earthquake_events WHERE origin_time > "{time}"'
            cursor.execute(sql)
            return [x[0] for x in cursor.fetchall()]
