import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import torch
from model import LSTMRegressor
from model import Predictor
from matplotlib import pyplot


def read_file(data_path):
    data = pd.read_csv(filepath_or_buffer=data_path, index_col="Date")
    return data


def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset) - look_back):
        a = dataset[i:(i + look_back), 0]
        dataX.append(a)
        dataY.append(dataset[i + look_back, 0])

    return np.array(dataX, dtype=np.float32), np.array(dataY, dtype=np.float32)


def create_data_dict(dataset, look_back=1):
    train_x, train_y = create_dataset(dataset, look_back)

    return {"x": torch.from_numpy(train_x).view(train_x.shape[0], train_x.shape[1], 1),
            "y": torch.from_numpy(train_y).view(train_y.shape[0], 1)}


if __name__ == '__main__':
    a = read_file("/Users/zxj/Downloads/bitcoin-price-prediction/bitcoin_price_Training - bitcoin_price.2013Apr-2017Aug.csv.csv")
    a = a[::-1]
    a['Close'].replace(0, np.nan, inplace=True)
    a['Close'].fillna(method='ffill', inplace=True)
    values = a['Close'].values.reshape(-1, 1)
    values = values.astype('float32')
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(values)
    train_size = int(len(scaled) * 0.8)
    test_size = len(scaled) - train_size
    train, test = scaled[0:train_size, :], scaled[train_size:len(scaled), :]
    train_dict = create_data_dict(train, 5)
    test_dict = create_data_dict(test, 5)
    model = LSTMRegressor(input_size=1,
                          hidden_size=128,
                          dropout_rate=0.5)

    predictor = Predictor(model=model,
                          train_data=train_dict,
                          test_data=test_dict,
                          batch_size=128)

    predictor.fit(150, 15)
    results = predictor.predict(predictor.test_loader).reshape(1, -1)[0]
    test_y = test_dict["y"].numpy().reshape(1, -1)[0]
    pyplot.plot(results, label='predict')
    pyplot.plot(test_y, label='true')
    pyplot.legend()
    pyplot.show()
