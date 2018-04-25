import json


if __name__ == '__main__':
    file_name = "bitcoin.json"
    with open(file_name, mode="r") as file:
        res = json.load(file)
        print(res)