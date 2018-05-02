from flask import Flask
from mysql_connector import DatabaseConnector
from datetime import datetime, timedelta
import json
from flask_cors import CORS
import os
from postgres_connector import PostGresConnector
from flask import request

app = Flask(__name__)
CORS(app)

connector = DatabaseConnector(host="cs336.ckksjtjg2jto.us-east-2.rds.amazonaws.com",
                              port=3306,
                              user="student",
                              password="cs336student",
                              db_name="CryptoNews")


postgres_connector = PostGresConnector(db_name="miandb",
                                       user="postgres",
                                       password="3968997",
                                       host="ec2-35-173-229-80.compute-1.amazonaws.com")


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
def show_information_of_certain_currency(date, currency_name):
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


@app.route('/predict/<currency_name>/<time>')
def predict_price_of_certain_currency(currency_name, time):
    cwd = os.getcwd()
    file_name = "{0}.json".format(currency_name.lower())
    data_path = os.path.join(cwd, "data", file_name)
    if not os.path.exists(data_path):
        data_path = os.path.join(cwd, "data", "bitcoin.json")

    with open(data_path, mode="r") as file:
        res = json.load(file)
        return json.dumps(res)


@app.route('/articles/<currency_name>/recent')
def get_related_articles_first_page(currency_name):
    today = datetime.today()
    before = datetime.today() - timedelta(days=3)
    num_dict = postgres_connector.query_number_of_news(currency_name,
                                                       before_time=before,
                                                       after_time=today)
    if num_dict["num_news"] == 0:
        return json.dumps({"number": 0, "result": []})

    res_dict = postgres_connector.query_currency_news(currency_name=currency_name,
                                  before_time=before,
                                  after_time=today,
                                  limit=10,
                                  offset=0)
    return json.dumps({"number": num_dict["num_news"], "result": res_dict["result"]})


@app.route('/articles/<currency_name>/following')
def get_related_articles_following(currency_name):
    today = datetime.today()
    before = datetime.today() - timedelta(days=3)
    page_size = int(request.args.get('pagesize'))
    page = int(request.args.get('page'))
    offset = (page - 1) * page_size
    res_dict = postgres_connector.query_currency_news(currency_name=currency_name,
                                  before_time=before,
                                  after_time=today,
                                  limit=page_size,
                                  offset=offset)
    return json.dumps({"result": res_dict["result"]})


