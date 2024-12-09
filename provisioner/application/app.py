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
    variant: ApplicationVariant
    version: str

    def __init__(self, variant: ApplicationVariant, version: str):
        self.variant = variant
        self.version = version

    @abstractmethod
    def preConfigureClusterLevelProperties(self, cluster: Cluster) -> None:
        pass

    @abstractmethod
    def nodeInstallApplication(self, node: Node) -> None:
        pass

APPLICATION_PARAMETER_GROUP_NAME = "Application"
APPLICATION_PARAMETER_GROUP_ID = "application"
APPLICATION_PARAMETERS: ParameterGroup = ParameterGroup(
    name=APPLICATION_PARAMETER_GROUP_NAME,
    id=APPLICATION_PARAMETER_GROUP_ID,
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
