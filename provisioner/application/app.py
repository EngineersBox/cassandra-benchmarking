from abc import ABC, abstractmethod
from enum import Enum
from .node import Node

class ApplicationVariant(Enum):
    CASSANDRA = "cassandra"
    MONGO_DB = "mongodb"
    SCYLLA = "scylla"
    ELASTICSEARCH = "elasticsearch"

class AbstractApplication(ABC):
    variant: ApplicationVariant
    version: str

    def __init__(self, variant: ApplicationVariant, version: str):
        self.variant = variant
        self.version = version

    @abstractmethod
    def nodeDetermineRoles(self, nodes: list[Node]) -> None:
        pass

