import psycopg2
import logging
from datetime import datetime


class PostGresConnector(object):
    def __init__(self, db_name, user, password, host="localhost", port="5432"):
        self.db_name = db_name
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.conn = connect_to_database(db_name, user, password, host, port)

    def execute_query(self, query, parameter_dict):
        if not self.conn:
            self.conn = connect_to_database(self.db_name, self.user, self.password, self.host, self.port)
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, parameter_dict)
                res = cursor.fetchall()
                return res

        except psycopg2.Error as e:
            logging.error('Failed to execute query!\n{0}'.format(e))
            return e

    def query_number_of_news(self, currency_name, before_time, after_time):
        query = """select count(title) from currency_news where currency_name=%(cur_name)s and date>= %(before)s and date <= %(after)s;"""
        parameter_dict = {"cur_name": currency_name,
                          "before": before_time,
                          "after": after_time}

        result = self.execute_query(query, parameter_dict)
        if isinstance(result, psycopg2.Error):
            return {"num_news": 0}
        else:
            return {"num_news": result[0][0]}

    def query_currency_news(self, currency_name, before_time, after_time, limit, offset):
        query = """select title, link, date from currency_news where currency_name=%(cur_name)s and \
    date>= %(before)s and date <= %(after)s ORDER BY date DESC limit %(limit)s offset %(offset)s """

        parameter_dict = {"cur_name": currency_name,
                          "before": before_time,
                          "after": after_time,
                          "limit": limit,
                          "offset": offset}
        result = self.execute_query(query, parameter_dict)
        if isinstance(result, psycopg2.Error):
            return {"result": "failure"}

        result_list = []
        for ele in result:
            if len(ele) != 3:
                continue
            title, link, date = ele
            date_string = date.strftime("%Y-%m-%d %H:%M")
            result_list.append({"link": link, "title": title, "date": date_string})

        return {"result": result_list}


def connect_to_database(db_name, user, password, host="localhost", port="5432"):
    try:
        conn = psycopg2.connect(dbname=db_name,
                                     user=user,
                                     password=password,
                                     host=host,
                                     port=port)
    except psycopg2.Error as e:
        print('Unable to connect!\n{0}'.format(e))
        conn = None

    return conn


if __name__ == '__main__':
    connector = PostGresConnector(db_name="miandb",
                                  user="postgres",
                                  password="3968997",
                                  host="ec2-35-173-229-80.compute-1.amazonaws.com")

    res_dict = connector.query_currency_news(currency_name="Bitcoin",
                                  before_time=datetime(2018, 4, 29),
                                  after_time=datetime(2018, 5, 2),
                                  limit=10,
                                  offset=0)
    for ele in res_dict["result"]:
        print(ele)