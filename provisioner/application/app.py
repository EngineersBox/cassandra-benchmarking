from abc import ABC, abstractmethod
from enum import Enum
from provisioner.structure.cluster import Cluster
from provisioner.parameters import ParameterGroup, Parameter
from provisioner.structure.node import Node
from provisioner.provisoner import TopologyProperties
import geni.portal as portal
from geni.rspec import pg

class ApplicationVariant(Enum):
    CASSANDRA = "cassandra", True
    MONGO_DB = "mongodb", True
    SCYLLA = "scylla", True
    ELASTICSEARCH = "elasticsearch", True,
    OTEL_COLLECTOR = "otel_collector", False

    def __str__(self) -> str:
        return "%s" % self.value[0]

    @staticmethod
    def provsionableMembers() -> list["ApplicationVariant"]:
        return list(filter(
            lambda e: e.value[1],
            ApplicationVariant._member_map_.values()
        ))

LOCAL_PATH = "/local"

class AbstractApplication(ABC):
    version: str

    @abstractmethod
    def __init__(self, version: str):
        self.version = version

    @classmethod
    @abstractmethod
    def variant(cls) -> ApplicationVariant:
        pass

    @abstractmethod
    def preConfigureClusterLevelProperties(self,
                                           cluster: Cluster,
                                           params: portal.Namespace,
                                           topologyProperties: TopologyProperties) -> None:
        pass

    def _unpackApplication(self, node: Node, url: str) -> None:
        node.instance.addService(pg.Install(
            url=url,
            path=LOCAL_PATH
        ))

    def bootstrapNode(self, node: Node, properties: dict[str, str]) -> None:
        # Bash env file
        env_file_content = f"""# Node configuration properties
APPLICATION_VARIANT={self.variant()}
APPLICATION_VERSION={self.version}
NODE_IP={node.getInterfaceAddress()}
"""
        for (k,v) in properties.items():
            env_file_content += f"\n{k}={v}"
        # Bash sourcable configuration properties that the
        # bootstrap script uses
        node.instance.addService(pg.Execute(
            shell="bash",
            command=f"echo \"{env_file_content}\" > {LOCAL_PATH}/node_config_properties.sh"
        ))
        # Install bootstrap systemd unit and run it
        node.instance.addService(pg.Execute(
            shell="bash",
            command=f"ln -s /{LOCAL_PATH}/units/bootstrap.service /etc/systemd/system/bootstrap.service && systemctl start bootstrap.service"
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
                    defaultValue=str(ApplicationVariant.CASSANDRA),
                    legalValues=[(str(app), app.name.title()) for app in ApplicationVariant.provsionableMembers()],
                    required=True
                ),
                Parameter(
                    name="application_version",
                    description="Version of the application",
                    typ=portal.ParameterType.STRING,
                    required=True
                ),
            ]
        )

    def validate(self, params: portal.Namespace) -> None:
        super().validate(params)

APPLICATION_PARAMETERS: ParameterGroup = ApplicationParameterGroup()
