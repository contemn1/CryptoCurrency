from pandas import read_csv
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import torch
from model import LSTMRegressor
from model import Predictor
from matplotlib import pyplot
from datetime import datetime, timedelta
import json

def read_data(path, columns=[1, 4, 5]):
    bitcoin_frame = read_csv(path, sep="\t")
    bitcoin_frame = bitcoin_frame
    df1 = bitcoin_frame.iloc[:, columns]
    return df1

def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back):
        a = dataset[i:(i + look_back)]
        dataX.append(a)
        dataY.append(dataset[i + look_back][0])
    return np.array(dataX, dtype=np.float32), np.array(dataY, dtype=np.float32)


def create_data_dict(dataset, look_back=1):
    train_x, train_y = create_dataset(dataset, look_back)

    return {"x": torch.from_numpy(train_x).view(train_x.shape[0], train_x.shape[1],  -1),
            "y": torch.from_numpy(train_y).view(train_y.shape[0], 1)}


if __name__ == '__main__':
    path = "/home/zxj/Downloads/crypto_data/Bitcoin_year.csv"
    columns = [1, 3, 4, 5]
    df1 = read_data(path, columns=columns)
    scaler = MinMaxScaler(feature_range=(0, 1))
    features = np.array(df1.values, dtype=np.float64)
    scaled_features = scaler.fit_transform(df1.values)
    data_min = scaler.data_min_[0]
    data_range = scaler.data_range_[0]
    train_size = 350
    valid_size = 10
    train, valid = scaled_features[0:train_size, :], scaled_features[train_size: train_size + valid_size, :]
    test = scaled_features[train_size + valid_size:, :]
    train_dict = create_data_dict(train, 4)
    valid_dict = create_data_dict(valid, 4)
    test_dict = create_data_dict(test, 2)
    model = LSTMRegressor(input_size=len(columns),
                          hidden_size=32,
                          dropout_rate=0.3
                          )

    predictor = Predictor(model=model,
                          train_data=train_dict,
                          test_data=valid_dict,
                          batch_size=64,
                          use_cuda=True)

    predictor.fit(400, 50)
    results = predictor.predict(predictor.test_loader).reshape(1, -1)[0]
    test_y = valid_dict["y"].numpy().reshape(1, -1)[0]
    print(test_y)
    axes = pyplot.gca()

    new_results = results * data_range + data_min
    new_test_y = test_y * data_range + data_min
    initial_date = datetime(2018, 4, 15)
    final_result = []
    for quote, predict in zip(new_test_y, new_results):
        initial_date = initial_date + timedelta(days=1)
        date_str = initial_date.strftime("%Y-%m-%d")
        final_result.append({"date": date_str, "quote": float(quote), "predict": float(predict)})

    res_dict = {"result": final_result}

    file = open("bitcoin.json", mode="w+")
    json.dump(res_dict, file)
    file.close()
    pyplot.plot(new_results, label='predict')
    pyplot.plot(new_test_y, label='true')
    pyplot.legend()
    pyplot.show()