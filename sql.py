import pymysql.cursors
import argparse
import personal

PASSWORD = personal.PASSWORD
USER = personal.USER

# Connect to the database
connection = pymysql.connect(host='localhost', user=USER, password=PASSWORD)


def create_db():
    with connection:
        with connection.cursor() as cursor:
            sql1 = "CREATE DATABASE IF NOT EXISTS web_scraper"
            cursor.execute(sql1)
            sql2 = "USE web_scraper"
            cursor.execute(sql2)
            sql3 = "CREATE TABLE IF NOT EXISTS test (" \
                   "id INT NOT NULL AUTO_INCREMENT," \
                   "magnitude FLOAT," \
                   "magnitude_unc FLOAT," \
                   "depth FLOAT," \
                   "depth_unc FLOAT," \
                   "PRIMARY KEY (id)" \
                   ")"
            cursor.execute(sql3)


def create(row):
    # connection is not autocommit by default. So you must commit to save
    # your changes.
    # connection.commit()
    with connection:
        with connection.cursor() as cursor:
            sql = "DESCRIBE test"
            cursor.execute(sql)
            result = cursor.fetchall()
            print(result)


def read(row):
    pass


def update(row, data):
    pass


def delete(index):
    pass
