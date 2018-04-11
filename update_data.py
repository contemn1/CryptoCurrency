import logging
import MySQLdb
from currency import Currency
from contextlib import closing


class DatabaseConnector(object):
    def __init__(self, host, port, user, password, db_name):
        self.db = MySQLdb.connect(host=host,
                                  port=port,
                                  user=user,
                                  passwd=password,
                                  db=db_name,
                                  use_unicode=True,
                                  )

    def execute_command(self, sql_command):
        with closing(self.db.cursor()) as my_cursor:
            try:
                my_cursor.execute(sql_command)
                return my_cursor.fetchall()

            except MySQLdb.Error as err:
                logging.error("Something went wrong: {0}".format(err))
                return []

    def get_all_currency(self, early_date, late_date):
        sql_command = f"""SELECT currency_name, quote, time FROM Value
         WHERE time >= '{early_date}' and time <= '{late_date}'"""
        return self.execute_command(sql_command)

    def get_certain_currency(self, early_date, late_date, cur_name):
        sql_command = f"""SELECT currency_name, quote, time FROM Value
         WHERE currency_name = '{cur_name}' and  time >= '{early_date}' and time <= '{late_date}'"""
        result = self.execute_command(sql_command)
        result = sorted(result, key=lambda x: x[2]) if result else []

        result_dict = {"currency_name": cur_name,
                       "currency_date": [ele[1] for ele in result],
                       "currency_quotes": [ele[2].strftime("%Y-%m-%d %H:%M:%S") for ele in result]}
        return result_dict

    def calculate_outlier(self, early_date, late_date):
        cur_map = {}
        for ele in self.get_all_currency(early_date, late_date):
            cur_name, quote, date = ele
            if cur_name not in cur_map:
                cur_map[cur_name] = [(quote, date)]
            else:
                cur_map[cur_name].append((quote, date))
        cur_map = {key: sorted(value, key=lambda x: x[1]) for key, value in cur_map.items()}

        _, standard_diff = calculate_diff_percentage(cur_map["Bitcoin"])
        for key, value in cur_map.items():
            latest_price, price_diff = calculate_diff_percentage(value)
            if price_diff * standard_diff < 0 or key == "Bitcoin":
                yield Currency(key, latest_price, round(price_diff * 100, 2))


def calculate_diff_percentage(value_array):
    price = [ele[0] for ele in value_array]
    price_diff = (price[-1] - price[0]) / price[0] if price[0] != 0 else -1.0
    return price[-1], price_diff


if __name__ == '__main__':
    connector = DatabaseConnector(host="cs336.ckksjtjg2jto.us-east-2.rds.amazonaws.com",
                                  port=3306,
                                  user="student",
                                  password="cs336student",
                                  db_name="CryptoNews")
    print(connector.get_certain_currency(early_date="2018-04-08",
                                         cur_name="Bitcoin",
                                         late_date="2018-04-09"))

    print(connector.get_certain_currency(early_date="2018-04-09",
                                         cur_name="Bitcoin",
                                         late_date="2018-04-10"))
