from flask import Flask
from update_data import DatabaseConnector
from datetime import datetime, timedelta
import json
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

connector = DatabaseConnector(host="cs336.ckksjtjg2jto.us-east-2.rds.amazonaws.com",
                              port=3306,
                              user="student",
                              password="cs336student",
                              db_name="CryptoNews")

curreny_names = {"Bitcoin", "Ethereum", "Ripple",
                 "Bitcoincash", "Eos", "Litecoin", "Cardano",
                 "Iota", "Neo", "Tron"}


@app.route('/outlier/<new_date>')
def show_user_profile(new_date):
    # show the user profile for that user
    time = datetime.strptime(new_date, "%Y-%m-%d")
    pre_date = time - timedelta(days=1)
    pre_date = pre_date.strftime("%Y-%m-%d")
    result = connector.calculate_outlier(pre_date, new_date)
    new_result = []
    for cur in result:
        cur.url = "{0}/{1}".format(cur.currency_name, new_date)
        new_result.append(cur)

    res_dict = {"result": new_result}
    return json.dumps(res_dict, default=lambda obj: obj.__dict__)


@app.route('/<currency_name>/<date>')
def show_information_of_certain_currency(currency_name, date):
    time = datetime.strptime(date, "%Y-%m-%d")
    pre_date = time - timedelta(days=1)
    pre_date = pre_date.strftime("%Y-%m-%d")
    return json.dumps(connector.get_certain_currency(early_date=pre_date,
                                                     cur_name=currency_name,
                                                     late_date=date))


@app.route('/top_currencies')
def show_top_currencies():
    result = {"result": connector.get_top_currency(curreny_names)}
    return json.dumps(result)