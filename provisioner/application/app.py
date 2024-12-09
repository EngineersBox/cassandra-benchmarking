from abc import ABC, abstractmethod
from enum import Enum
from provisioner.application.cluster import Cluster
from provisioner.parameters import ParameterGroup, Parameter
from .node import Node
import geni.portal as portal
from geni.rspec import pg

class ApplicationVariant(Enum):
    CASSANDRA = "cassandra"
    MONGO_DB = "mongodb"
    SCYLLA = "scylla"
    ELASTICSEARCH = "elasticsearch"

LOCAL_PATH = "/local"

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
    def preConfigureClusterLevelProperties(self, cluster: Cluster, params: portal.Namespace) -> None:
        pass

    def _unpackApplication(self, node: Node, url: str) -> None:
        node.instance.addService(pg.Install(
            url=url,
            path=LOCAL_PATH
        ))

    def _invokeInstaller(self, node: Node, properties: dict[str, str]) -> None:
        # Bash env file
        env_file_content = f"""# Node configuration properties
APPLICATION_VARIANT={self.variant()}
APPLICATION_VERSION={self.version}
"""
        for (k,v) in properties.items():
            env_file_content = env_file_content.join(f"\n{k}={v}")
        # Bash sourcable configuration properties that the
        # install script uses
        node.instance.addService(pg.Execute(
            shell="bash",
            command=f"echo \"{env_file_content}\" > {LOCAL_PATH}/node_config_properties.sh"
        ))
        # Script to handle node-specific application installation
        # and configuration
        node.instance.addService(pg.Execute(
            shell="bash",
            command=f"{LOCAL_PATH}/install.sh"
        ))

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
