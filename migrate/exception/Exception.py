class NoDataBaseFinded(Exception):
    def __init__(self):
        super().__init__('Can\'t find database credentials')

