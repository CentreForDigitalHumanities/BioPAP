class BaseClass():

    raw = None
    processed = None

    def __init__(self):
        pass

    @property
    def raw_data(self):
        return self.raw

    @property
    def processed_data(self):
        return self.processed