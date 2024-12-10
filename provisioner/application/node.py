from dataclasses import dataclass
from typing import Optional
import geni.rspec.pg as pg 

@dataclass
class Node:
    id: str
    instance: pg.RawPC
    size: str
    interface: pg.Interface
    config: Optional[str] = None
