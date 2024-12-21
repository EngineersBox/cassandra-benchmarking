from dataclasses import dataclass, field
import geni.rspec.pg as pg

@dataclass
class TopologyProperties:
    collectorInterface: pg.Interface
    nodeInterfaces: list[pg.Interface] = field(default_factory=list)
