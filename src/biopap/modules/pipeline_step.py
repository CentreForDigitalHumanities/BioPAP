from dataclasses import dataclass
from typing import Any

@dataclass
class PipelineStep:
    Module: Any
    Cfg: dict
    Order: int

    standalone_module = False

    def __repr__(self):
        return f"{self.Order}: {self.Module.__name__} ← {self.Cfg}"

    def as_dict(self):
        return  {
            'module': self.Module.__name__,
            'cfg': self.Cfg,
            'order': self.Order,
            }

