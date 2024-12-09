from dataclasses import dataclass
from .rack import Rack

@dataclass
class DataCentre:
    name: str
    racks: dict[str, Rack]
