from dataclasses import dataclass
from .app import AbstractApplication
from .node import Node

@dataclass
class Cluster:
    application: AbstractApplication
    nodes: list[Node] = []
