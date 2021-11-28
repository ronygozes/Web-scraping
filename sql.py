import pymysql.cursors
import personal

from configs import sql_config

PASSWORD = personal.PASSWORD
USER = personal.USER


def create_db():
    with pymysql.connect(host='localhost', user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.CREATE_DATABASE)


def create_tables():
    with pymysql.connect(host='localhost', user=USER, password=PASSWORD) as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql_config.USE)
            cursor.execute(sql_config.CREATE_REVIEW)
            cursor.execute(sql_config.CREATE_CONTRIBUTOR)
            cursor.execute(sql_config.CREATE_FE_REGION)
            cursor.execute(sql_config.CREATE_CATALOG)
            cursor.execute(sql_config.CREATE_EARTHQUAKES)


def add_review_status(cursor, dic):
    # sql = f"INSERT IGNORE INTO review_status VALUES ({dic['review_status']})"
    sql = sql_config.INSERT_STR.format(table='review_status', column='review_status', value=dic['review_status'])
    print(sql)
    cursor.execute(sql)
    # sql2 = f"SELECT id FROM review_status WHERE review_status={dic['review_status']}"
    sql2 = sql_config.SELECT_ID.format(table='review_status', field='review_status', value=dic['review_status'])
    cursor.execute(sql2)
    id = cursor.fetchone()[0]
    del dic['review_status']
    dic['review_status_id'] = id


def add_fe_region(cursor, dic):
    # sql = f"INSERT IGNORE INTO fe_region VALUES ({dic['fe_region']})"
    sql = sql_config.INSERT_STR.format(table='fe_region', column='fe_region', value=dic['fe_region'])
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='fe_region', field='fe_region', value=dic['fe_region'])
    cursor.execute(sql2)
    id = cursor.fetchone()[0]
    del dic['fe_region']
    dic['fe_region_id'] = id


def add_catalog(cursor, dic):
    # sql = f"INSERT IGNORE INTO catalog VALUES ({dic['catalog']})"
    sql = sql_config.INSERT_STR.format(table='catalog', column='catalog', value=dic['catalog'])
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='catalog', field='catalog', value=dic['catalog'])
    cursor.execute(sql2)
    id = cursor.fetchone()[0]
    del dic['catalog']
    dic['catalog_id'] = id


def add_contributor(cursor, dic):
    # sql = f"INSERT IGNORE INTO contributor VALUES ({dic['contributor']})"
    sql = sql_config.INSERT_STR.format(table='contributor', column='contributor', value=dic['contributor'])
    cursor.execute(sql)
    sql2 = sql_config.SELECT_ID.format(table='contributor', field='contributor', value=dic['contributor'])
    cursor.execute(sql2)
    id = cursor.fetchone()[0]
    del dic['contributor']
    dic['contributor_id'] = id


def add_earthquake_event(cursor, dic):
    # sql = f"INSERT IGNORE INTO earthquake_events ({', '.join(dic.keys())})" \
    #       f" VALUES ({', '.join(['%s'] * len(dic))})"
    # sql = sql_config.INSERT_STR.format(table='earthquake_events', column=', '.join(dic.keys()),
    #                                    value=', '.join(['%s'] * len(dic)))
    values = ["'" + str(value) + "'" for value in dic.values()]
    values[0] = values[0][1:]
    values[-1] = values[-1][:-1]
    sql = sql_config.INSERT_STR.format(table='earthquake_events', column=', '.join(dic.keys()),
                                       value=", ".join(values))
    print('sql',sql)
    cursor.execute(sql)


def add_batch(dicts, batch_size):
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


# create_db()
# create_tables()
# dicts = [
#     dict(event_key='pr1234', magnitude=3.4, magnitude_uncertainty=0.1, location='abcdefg', location_uncertainty_km=2.4,
#          depth_uncertainty_km=2.6, depth_km=111, origin_time='2021-11-25 16:28:54.922329', num_of_stations=14,
#          num_of_phases=57, minimum_distance_km=54, travel_time_residual_sec=24, azimuthal_gap_deg=1, fe_region='dffghg',
#          review_status='automated', catalog='us', contributor='us'),
#     dict(event_key='ok4857', magnitude=3.4, magnitude_uncertainty=0.1, location='abcdefg', location_uncertainty_km=2.4,
#          depth_uncertainty_km=2.6, depth_km=111, origin_time='2021-11-25 17:05:31.399952', num_of_stations=14,
#          num_of_phases=57, minimum_distance_km=54, travel_time_residual_sec=24, azimuthal_gap_deg=1, fe_region='dffghg',
#          review_status='reviewed', catalog='us', contributor='us')
# ]

# add_batch(dicts, 3)


def read(row):
    pass


def update(row, data):
    pass


def delete(index):
    pass
