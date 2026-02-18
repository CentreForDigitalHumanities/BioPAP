from abc import ABC, abstractmethod
from typing import Union, Optional

class BaseClass(ABC):

    raw = None
    processed = None
    verbose = None

    def __init__(self):
        pass

    @property
    def raw_data(self):
        return self.raw

    @property
    def processed_data(self):
        return self.processed