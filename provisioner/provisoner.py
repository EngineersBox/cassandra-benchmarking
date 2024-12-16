import geni.portal as portal
import geni.rspec.pg as pg
import uuid
from .application.app import *
from .application.node import Node
from .application.cluster import Cluster
from .application.rack import Rack
from .application.datacentre import DataCentre
from .application.bundle.cassandra import CassandraApplication
from .application.bundle.mongodb import MongoDBApplication
from .application.bundle.elasticsearch import ElasticsearchApplication
from .application.bundle.scylla import ScyllaApplication

NODE_IPV4_FORMAT = "10.50.0.%d"
NODE_IPV4_NETMASK = "255.255.255.0"
NODE_INTERFACE_NAME_FORMAT = "if%d"
NODE_PHYSICAL_INTERFACE_FORMAT = "eth%d"

APPLICATION_BINDINGS: dict[ApplicationVariant, type[AbstractApplication]] = {
    CassandraApplication.variant(): CassandraApplication,
    MongoDBApplication.variant(): MongoDBApplication,
    ElasticsearchApplication.variant(): ElasticsearchApplication,
    ScyllaApplication.variant(): ScyllaApplication
}

# TODO: How do we get creds like docker registry access tokens
#       onto nodes without baking them into publicly visible
#       stuff (i.e. archives or code)?
class Provisioner:

    def nodeProvision(self, i: int, request: pg.Request, params: portal.Namespace) -> Node:
        id = str(uuid.uuid4())
        node_vm = pg.RawPC(id)
        node_vm.disk_image = params.node_disk_image
        request.addResource(node_vm)
        iface: pg.Interface = node_vm.addInterface(NODE_INTERFACE_NAME_FORMAT % i)
        # iface.component_id = Provisioner.NODE_PHYSICAL_INTERFACE_FORMAT % i
        address: pg.IPv4Address = pg.IPv4Address(
            NODE_IPV4_FORMAT % i,
            NODE_IPV4_NETMASK
        )
        iface.addAddress(address)
        return Node(
            id=id,
            instance=node_vm,
            size=params.node_size,
            interface=iface
        )

    def rackProvision(self, i: int, _params: portal.Namespace) -> Rack:
        return Rack(
            name="rack-%d" % i,
            nodes=[]
        )

    def datacentreProvision(self, i: int, params: portal.Namespace) -> DataCentre:
        return DataCentre(
            name="dc-%d" % i,
            racks={}
        )

    def provisionLAN(self, request: pg.Request, params: portal.Namespace, cluster: Cluster) -> None:
        lan: pg.LAN = pg.LAN("LAN")
        for node in cluster.nodesGenerator():
            lan.addInterface(node.interface)
        lan.connectSharedVlan(params.vlan_type)
        request.addResource(lan)

    def partitionDataCentres(self, request: pg.Request, params: portal.Namespace) -> dict[str, DataCentre]:
        print("Partitioning nodes into datacentres and racks")
        datacentres: dict[str, DataCentre] = {}
        dc_idx: int = 0
        rack_idx: int = 0
        node_idx: int = 0
        for _ in range(params.dc_count):
            dc: DataCentre = self.datacentreProvision(dc_idx, params)
            datacentres[dc.name] = dc
            for _ in range(params.racks_per_dc):
                rack: Rack = self.rackProvision(rack_idx, params)
                dc.racks[rack.name] = rack
                for _ in range(params.nodes_per_rack):
                    rack.nodes.append(self.nodeProvision(node_idx, request, params))
                    node_idx += 1
                rack_idx += 1
            dc_idx += 1
            rack_idx = 0
        return datacentres

    def bootstrapDB(self, request: pg.Request, params: portal.Namespace) -> Cluster:
        app_variant: ApplicationVariant = ApplicationVariant(ApplicationVariant._member_map_[str(params.application).upper()])
        app: AbstractApplication = APPLICATION_BINDINGS[app_variant](params.application_version)
        cluster: Cluster = Cluster()
        cluster.datacentres = self.partitionDataCentres(request, params)
        app.preConfigureClusterLevelProperties(cluster, params)
        # Addresses are assigned in previous loop, we need to know
        # them all before installing as each node should know the
        # addresses of all other nodes
        for node in cluster.nodesGenerator():
            print(f"Installing {params.application} on node {node.id}")
            app.nodeInstallApplication(node) 
        self.provisionLAN(request, params, cluster)
        return cluster

    def bootstrapCollector(self, request: pg.Request, params: portal.Namespace, cluster: Cluster) -> None:
        pass
