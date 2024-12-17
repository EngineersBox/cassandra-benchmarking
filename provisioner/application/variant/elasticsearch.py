from provisioner.application.app import AbstractApplication, ApplicationVariant
from provisioner.structure.node import Node
from provisioner.structure.cluster import Cluster
from provisioner.provisoner import TopologyProperties
import geni.portal as portal

class ElasticsearchApplication(AbstractApplication):

    def __init__(self, version: str):
        super().__init__(version)

    @classmethod
    def variant(cls) -> ApplicationVariant:
        return ApplicationVariant.ELASTICSEARCH

    def preConfigureClusterLevelProperties(self,
                                           cluster: Cluster,
                                           params: portal.Namespace,
                                           topologyProperties: TopologyProperties) -> None:
        super().preConfigureClusterLevelProperties(
            cluster,
            params,
            topologyProperties
        )
        # TODO: Implement this

    def nodeInstallApplication(self, node: Node) -> None:
        # TODO: Implement this
        pass
