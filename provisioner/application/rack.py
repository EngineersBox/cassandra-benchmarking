from dataclasses import dataclass
from .node import Node

@dataclass
class Rack:
    name: str
    nodes: list[Node]
