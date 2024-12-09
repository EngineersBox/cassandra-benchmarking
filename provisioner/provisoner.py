import geni.portal as portal
import geni.rspec.pg as pg

from .application.app import *
from .application.node import Node
from .application.cluster import Cluster
from .application.bundle.cassandra import CassandraApplication, DataCentre
from .application.bundle.mongodb import MongoDBApplication
from .application.bundle.elasticsearch import ElasticsearchApplication
from .application.bundle.scylla import ScyllaApplication

class Provisioner:

    NODE_IPV4_FORMAT = "10.50.0.%d"
    NODE_IPV4_NETMASK = "255.255.255.0"
    NODE_INTERFACE_NAME_FORMAT = "if%d"
    NODE_PHYSICAL_INTERFACE_FORMAT = "eth%d"

    def nodeProvision(self, i: int, request: pg.Request, params: portal.Namespace) -> Node:
        node_vm = pg.RawPC("node%d" % i)
        node_vm.disk_image = params.node_disk_image
        request.addResource(node_vm)
        iface = node_vm.addInterface(Provisioner.NODE_INTERFACE_NAME_FORMAT % i)
        # iface.component_id = Provisioner.NODE_PHYSICAL_INTERFACE_FORMAT % i
        address = pg.IPv4Address(Provisioner.NODE_IPV4_FORMAT % i, Provisioner.NODE_IPV4_NETMASK)
        iface.addAddress(address)
        return Node(
            node_vm,
            params.node_size,
            iface
        )

    def provisionLAN(self, request: pg.Request, params: portal.Namespace, cluster: Cluster) -> None:
        lan: pg.LAN = pg.LAN("LAN")
        for node in cluster.nodes:
            lan.addInterface(node.interface)
        lan.connectSharedVlan(params.vlan_type)
        request.addResource(lan)

    def partitionDataCentres(self, params: portal.Namespace) -> dict[str, DataCentre]:
        pass

    def bootstrapDB(self, request: pg.Request, params: portal.Namespace) -> Cluster:
        app_variant: ApplicationVariant = ApplicationVariant(ApplicationVariant._member_map_[params.cluster_application])
        app: AbstractApplication;
        if app_variant == ApplicationVariant.CASSANDRA:
            app = CassandraApplication(params.cluster_application_version)
        elif app_variant == ApplicationVariant.MONGO_DB:
            app = MongoDBApplication(params.cluster_application_version)
        elif app_variant == ApplicationVariant.SCYLLA:
            app = ScyllaApplication(params.cluster_application_version)
        elif app_variant == ApplicationVariant.ELASTICSEARCH:
            app = ElasticsearchApplication(params.cluster_application_version)
        else:
            raise ValueError(f"Unknown application type: {app_variant}")
        cluster: Cluster = Cluster()
        for i in range(params.node_count):
            cluster.nodes.append(self.nodeProvision(i, request, params))
        app.preConfigureClusterLevelProperties(cluster)
        # Addresses are assigned in previous loop, we need to know
        # them all before installing as each node should know the
        # addresses of all other nodes
        for node in cluster.nodes:
            app.nodeInstallApplication(node)
        
        self.provisionLAN(request, params, cluster)
        return cluster

    def bootstrapCollector(self, request: pg.Request, params: portal.Namespace, cluster: Cluster) -> None:
        pass
