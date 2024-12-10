from abc import ABC, abstractmethod
from enum import Enum
from provisioner.application.cluster import Cluster
from provisioner.parameters import ParameterGroup, Parameter
from .node import Node
import geni.portal as portal

class ApplicationVariant(Enum):
    CASSANDRA = "cassandra"
    MONGO_DB = "mongodb"
    SCYLLA = "scylla"
    ELASTICSEARCH = "elasticsearch"

class AbstractApplication(ABC):
    version: str

    @abstractmethod
    def __init__(self, version: str):
        self.version = version

    @abstractmethod
    @classmethod
    def variant(cls) -> ApplicationVariant:
        pass

    @abstractmethod
    def preConfigureClusterLevelProperties(self, cluster: Cluster) -> None:
        pass

    @abstractmethod
    def nodeInstallApplication(self, node: Node) -> None:
        pass

class ApplicationParameterGroup(ParameterGroup):

    @classmethod
    def name(cls) -> str:
        return "Application"

    @classmethod
    def id(cls) -> str:
        return "application"

    def __init__(self):
        super().__init__(
            parameters=[
                Parameter(
                    name="application",
                    description="Database application to install",
                    typ=portal.ParameterType.STRING,
                    defaultValue=ApplicationVariant.CASSANDRA,
                    legalValues=[(app.value, app.name.title()) for app in ApplicationVariant]
                ),
            ]
        )

    def validate(self) -> None:
        super().validate()

APPLICATION_PARAMETERS: ParameterGroup = ApplicationParameterGroup()
