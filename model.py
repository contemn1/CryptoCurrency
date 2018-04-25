from torch import nn
from torch.utils.data import TensorDataset
from torch.utils.data import DataLoader
from torch.autograd import Variable
import torch.optim as optim
import numpy as np
import copy


class Predictor(object):
    def __init__(self, model, train_data, test_data, batch_size=64, use_cuda=False, l2_reg=0.001):
        self.use_cuda = use_cuda
        self.model = model.cuda() if use_cuda else model
        self.batch_size = batch_size
        self.training_set = TensorDataset(data_tensor=train_data["x"], target_tensor=train_data["y"])
        self.test_set = TensorDataset(data_tensor=test_data["x"], target_tensor=test_data["y"])
        self.train_loader = self.init_dataloader(self.training_set)
        self.test_loader = self.init_dataloader(self.test_set)
        self.loss_fn = nn.MSELoss().cuda() if use_cuda else nn.MSELoss()
        self.optimizer = optim.Adam(self.model.parameters(),
                                    weight_decay=l2_reg)

    def init_dataloader(self, dataset):
        return DataLoader(dataset=dataset,
                          batch_size=self.batch_size,
                          pin_memory=self.use_cuda,
                          shuffle=False)

    def train_epoch(self):
        self.model.train()
        all_costs = []
        for x_batch, y_batch in self.train_loader:
            x_batch = x_batch.view(x_batch.size(1), x_batch.size(0), -1)
            # forward
            if self.use_cuda:
                x_batch = x_batch.cuda()
                y_batch = y_batch.cuda()

            x_batch = Variable(x_batch)
            y_batch = Variable(y_batch)
            output = self.model(x_batch)
            # loss
            loss = self.loss_fn(output, y_batch)
            loss_data = loss.data.cpu()[0] if self.use_cuda else loss.data[0]
            all_costs.append(loss_data)
            # backward
            self.optimizer.zero_grad()
            loss.backward()
            # Update parameters
            self.optimizer.step()

        return np.mean(all_costs)

    def calculate_validation_cost(self, dev_loader=None):
        self.model.eval()
        if not dev_loader:
            dev_loader = self.test_loader

        all_costs = []
        for x_batch, y_batch in dev_loader:
            x_batch = x_batch.view(x_batch.size(1), x_batch.size(0), -1)
            # forward
            if self.use_cuda:
                x_batch = x_batch.cuda()
                y_batch = y_batch.cuda()

            x_batch = Variable(x_batch)
            y_batch = Variable(y_batch)
            output = self.model(x_batch)
            loss = self.loss_fn(output, y_batch)
            loss_data = loss.data.cpu()[0] if self.use_cuda else loss.data[0]
            all_costs.append(loss_data)

        return np.mean(all_costs)

    def predict(self, dev_loader):
        self.model.eval()
        yhat = np.array([])
        for Xbatch, _ in dev_loader:
            Xbatch = Xbatch.view(Xbatch.size(1), Xbatch.size(0), -1)
            if self.use_cuda:
                Xbatch = Xbatch.cuda()

            Xbatch = Variable(Xbatch, volatile=True)
            output = self.model(Xbatch)
            yhat = np.append(yhat,
                             output.data.cpu().numpy())
        yhat = np.vstack(yhat)
        return yhat

    def fit(self, epoches, maximum_failure):
        train_cost = []
        dev_cost = []
        num_failed = 0
        best_cost = 1
        for _ in range(epoches):
            current_train_cost = self.train_epoch()
            current_valid_cost = self.calculate_validation_cost()
            if current_valid_cost < best_cost:
                best_cost = current_valid_cost
                best_model = copy.deepcopy(self.model)
                num_failed = 0
            else:
                num_failed += 1

            if num_failed > maximum_failure:
                break

            train_cost.append(current_train_cost)
            dev_cost.append(current_valid_cost)
        print(train_cost)
        print(dev_cost)
        self.model = best_model


class LSTMRegressor(nn.Module):
    def __init__(self, input_size, hidden_size, dropout_rate=0.5, layer=1):
        super(LSTMRegressor, self).__init__()
        self.rnn = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                           num_layers=layer, dropout=dropout_rate)
        self.init_rnn()
        self.dropout_layer = nn.Dropout(dropout_rate)
        self.linear = nn.Linear(layer * hidden_size, 1)

    def forward(self, data):
        _, (last_hidden, _) = self.rnn(data)
        last_hidden = last_hidden[0]
        dropped_out_hidden = self.dropout_layer(last_hidden)
        result = self.linear(dropped_out_hidden)
        return result

    def init_rnn(self):
        for name, param in self.rnn.named_parameters():
            if 'bias' in name:
                nn.init.constant(param, 0.0)
            elif 'weight' in name:
                nn.init.xavier_normal(param)
