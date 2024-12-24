from abc import ABC, abstractmethod
from enum import Enum
from provisioner.collector.collector import OTELFeature
from provisioner.structure.cluster import Cluster
from provisioner.parameters import ParameterGroup, Parameter
from provisioner.structure.node import Node
from provisioner.topology import TopologyProperties
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

LOCAL_PATH = "/var/lib"

class AbstractApplication(ABC):
    version: str
    topologyProperties: TopologyProperties
    collectorFeatures: set[OTELFeature]

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
        self.topologyProperties = topologyProperties
        self.collectorFeatures = params.collector_features

    def unpackTar(self, node: Node, url: str) -> None:
        node.instance.addService(pg.Install(
            url=url,
            path=LOCAL_PATH
        ))

    def _writeEnvFile(self,
                      node: Node,
                      properties: dict[str, str]) -> None:
        collector_address: str = self.topologyProperties.collectorInterface.addresses[0].address
        # Ensure the collector exports data for enabled features
        for feat in self.collectorFeatures:
            properties[f"OTEL_{str(feat).upper()}_EXPORTER"] = "otlp"
        if OTELFeature.TRACES in self.collectorFeatures:
            properties["OTEL_TRACES_EXPORTER"] = "always_on"
        # Bash env file
        env_file_content = f"""# Node configuration properties
APPLICATION_VARIANT={self.variant()}
APPLICATION_VERSION={self.version}

EBPF_NET_INTAKE_HOST={collector_address}
EBPF_NET_INTAKE_PORT=8000

OTEL_EXPORTER_OTLP_ENDPOINT=http://{collector_address}:4318
OTEL_SERVICE_NAME={node.id}
OTEL_RESOURCE_ATTRIBUTES=application={self.variant()}

NODE_IP={node.getInterfaceAddress()}
"""
        for (k,v) in properties.items():
            env_file_content += f"\n{k}={v}"
        # Bash sourcable configuration properties that the
        # bootstrap script uses as well as docker containers
        node.instance.addService(pg.Execute(
            shell="bash",
            command=f"echo \"{env_file_content}\" > {LOCAL_PATH}/node_env"
        ))
        # Replace template var for pushing logs
        node.instance.addService(pg.Execute(
            shell="bash",
            command=f"sed -i \"s/@@COLLECTOR_ADDRESS@@/{collector_address}/g\" {LOCAL_PATH}/config/otel/otel-instance.config.yaml"
        ))

    def bootstrapNode(self,
                      node: Node,
                      properties: dict[str, str]) -> None:
        self._writeEnvFile(
            node,
            properties
        )
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
