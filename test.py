import json
import os


if __name__ == '__main__':
    currency_name = "bitcoin"
    cwd = os.getcwd()
    file_name = "{0}.json".format(currency_name.lower())
    data_path = os.path.join(cwd, "data", file_name)
    print(data_path)