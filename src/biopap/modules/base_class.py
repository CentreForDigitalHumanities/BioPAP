class BaseClass():

    raw = None
    processed = None
    verbose = False

    def __init__(self, verbose=False):
        self.verbose = verbose

    @property
    def raw_data(self):
        return self.raw

    @property
    def processed_data(self):
        return self.processed