class Currency(object):
    def __init__(self, currency_name, quote, rate):
        self.currency_name = currency_name
        self.quote = quote
        self.rate = rate
        self.url = ""