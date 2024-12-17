from provisioner.application.app import AbstractApplication, ApplicationVariant
from provisioner.structure.cluster import Cluster
from provisioner.structure.node import Node
from provisioner.provisoner import TopologyProperties
import geni.portal as portal

class OTELCollector(AbstractApplication):

    def __init__(self, version: str):
        super().__init__(version)

    @classmethod
    def variant(cls) -> ApplicationVariant:
        return ApplicationVariant.OTEL_COLLECTOR

    def preConfigureClusterLevelProperties(self,
                                           cluster: Cluster,
                                           params: portal.Namespace,
                                           topologyProperties: TopologyProperties) -> None:
        return super().preConfigureClusterLevelProperties(cluster, params, topologyProperties)

    def nodeInstallApplication(self, node: Node) -> None:
        return super().nodeInstallApplication(node)
