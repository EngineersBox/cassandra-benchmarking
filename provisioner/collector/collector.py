from dataclasses import dataclass
from provisioner.structure.node import Node

@dataclass
class Collector:
    node: Node
