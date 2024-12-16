from dataclasses import dataclass
from .rack import Rack

@dataclass
class DataCentre:
    name: str
    racks: dict[str, Rack]

    def __hash__(self) -> int:
        return self.name.__hash__()
