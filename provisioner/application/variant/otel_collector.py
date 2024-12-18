from provisioner.application.app import AbstractApplication, ApplicationVariant
from provisioner.structure.cluster import Cluster
from provisioner.structure.node import Node
from provisioner.provisoner import TopologyProperties
import geni.portal as portal

class OTELCollector(AbstractApplication):
    ycsb_version: str
    cluster_application: str

    def __init__(self, version: str):
        super().__init__(version)

    @classmethod
    def variant(cls) -> ApplicationVariant:
        return ApplicationVariant.OTEL_COLLECTOR

    def preConfigureClusterLevelProperties(self,
                                           cluster: Cluster,
                                           params: portal.Namespace,
                                           topologyProperties: TopologyProperties) -> None:
        super().preConfigureClusterLevelProperties(
            cluster,
            params,
            topologyProperties
        )
        self.ycsb_version = params.ycsb_version
        self.cluster_application = params.application

    def nodeInstallApplication(self, node: Node) -> None:
        super().nodeInstallApplication(node)
        self.unpackTar(
            node,
            f"https://github.com/EngineersBox/cassandra-benchmarking/releases/{OTELCollector.variant()}-{self.version}/{OTELCollector.variant()}.tar.gz"
        )
        self.unpackTar(
            node,
            f"https://github.com/brianfrankcooper/YCSB/releases/download/{self.ycsb_version}/ycsb-{self.ycsb_version}.tar.gz"
        )
        all_ips: list[str] = []
        for iface in self.topologyProperties.nodeInterfaces:
            all_ips.append(iface.addresses[0].address)
        all_ips_prop: str = " ".join([f"\"{address}\"" for address in all_ips]) 
        self.bootstrapNode(
            node,
            {
                "YCSB_VERSION": self.ycsb_version,
                "CLUSTER_APPLICATION": self.cluster_application,
                "NODE_ALL_IPS": f"({all_ips_prop})"
            },
        )
