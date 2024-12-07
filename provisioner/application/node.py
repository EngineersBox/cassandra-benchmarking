from dataclasses import dataclass
import geni.rspec.pg as pg 

@dataclass
class Node:
    instance: pg.RawPC
    size: str
    interface: pg.Interface
    roles: list[str] = []
