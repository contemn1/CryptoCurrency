import logging
import MySQLdb
import sys
from currency import Currency
import json
from contextlib import closing
from datetime import datetime, timedelta
import numpy as np

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
        sql_command = """SELECT currency_name, quote, time FROM Value
         WHERE time >= '{0}' and time <= '{1}'""".format(early_date, late_date)
        return self.execute_command(sql_command)

    def get_certain_currency(self, early_date, late_date, cur_name):
        sql_command = """SELECT currency_name, quote, time FROM Value
         WHERE currency_name = '{0}' and  time >= '{1}' and time <= '{2}'""".format(cur_name, early_date, late_date)
        result = self.execute_command(sql_command)
        result = sorted(result, key=lambda x: x[2]) if result else []
        cur_quotes = [ele[1] for ele in result]
        cur_date = [ele[2].strftime("%Y-%m-%d %H:%M:%S") for ele in result]
        cur_res = zip(cur_date, cur_quotes)
        cur_res = [{"date": date, "quote": quote} for date, quote in cur_res]

        result_dict = {"result": cur_res}
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

    def get_top_currency(self, curreny_names):
        early_date = datetime.today().strftime("%Y-%m-%d")
        late_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql_command = """SELECT currency_name, quote, time FROM Value WHERE time >= '{0}' and time <= '{1}'""".format(early_date, late_date)
        result = self.execute_command(sql_command)
        result = [ele for ele in result if ele[0] in curreny_names]
        result = sorted(result, key=lambda x: x[2]) if result else []
        new_result = [{"currency": ele[0], "open":float(ele[1]), "latest": "", "rate": ""} for ele in result[:10]]
        latest_prices = [float(ele[1]) for ele in result[-10:]]
        for index, item in enumerate(new_result):
            item["latest"] = latest_prices[index]
            item["rate"] = ((latest_prices[index] - item["open"]) / item["open"])*100

        return new_result

    def predict_currency_price(self, currency_name, date):
        early_date = datetime.strptime(date, "%Y-%m-%d") - timedelta(days=5)
        early_date = early_date.strftime("%Y-%m-%d")
        sql_command = """SELECT currency_name, quote FROM Value WHERE currency_name='{0}'  and time >= '{1}'and time <= '{2}' ORDER BY time """.format(currency_name, early_date, date)
        result = self.execute_command(sql_command)
        quotes = np.array([ele[1] for ele in result])
        noise = np.random.uniform(0.9, 1.1, len(quotes))
        predict_quotes = quotes * noise
        final_result = []
        for index in range(len(quotes)):
            final_result.append({"quotes": quotes[index], "predicted_quotes": predict_quotes[index]})

        results = {"currency": currency_name,
                   "result": final_result}

        return results


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
    curreny_names = {"Bitcoin", "Ethereum", "Ripple",
                     "Bitcoincash", "Eos", "Litecoin", "Cardano",
                      "Iota", "Neo", "Tron"}
    res = connector.get_top_currency(curreny_names)
    print((res))