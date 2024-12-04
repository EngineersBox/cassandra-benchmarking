from dataclasses import dataclass
from enum import Enum
from typing import Optional
import geni.portal as portal
import geni.rspec.pg as pg 

PARAMETER_GROUP_CLUSTER = "cluster"
PARAMETER_GROUP_NODE = "node"

@dataclass
class Node:
    instance: pg.RawPC
    size: str
    interface: pg.Interface
    roles: list[str] = []

class ApplicationVariant(Enum):
    CASSANDRA = "cassandra"
    MONGO_DB = "mongodb"
    SCYLLA = "scylla"
    ELASTICSEARCH = "elasticsearch"

@dataclass
class Application:
    variant: ApplicationVariant
    version: str

@dataclass
class Cluster:
    application: Application
    nodes: list[Node] = []

# === COLLECTOR === #

def bootstrapCollector(request: pg.Request, params: portal.Namespace, cluster: Cluster) -> None:
    pass

# === INSTANCE === #

NODE_IPV4_FORMAT = "10.50.0.%d"
NODE_IPV4_NETMASK = "255.255.255.0"
NODE_INTERFACE_NAME_FORMAT = "if%d"
NODE_PHYSICAL_INTERFACE_FORMAT = "eth%d"

def nodeProvision(i: int, request: pg.Request, params: portal.Namespace) -> Node:
    node_vm = pg.RawPC("node%d" % i)
    node_vm.disk_image = params.node_disk_image
    request.addResource(node_vm)
    iface = node_vm.addInterface(NODE_INTERFACE_NAME_FORMAT % i)
    # iface.component_id = NODE_PHYSICAL_INTERFACE_FORMAT % i
    address = pg.IPv4Address(NODE_IPV4_FORMAT % i, NODE_IPV4_NETMASK)
    iface.addAddress(address)
    return Node(
        node_vm,
        params.node_size,
        iface
    )

def nodeInstallApplication(cluster: Cluster, node: Node) -> None:
    node.instance.addService(pg.Install(
        # TODO: Make sure this URL is correct and constructed properly
        url=f"https://github.com/EngineersBox/cassandra-benchmarking/releases/{cluster.application.version}/{cluster.application}.tar.gz",
        path="/local"
    ))
    node_ips = " ".join([_node.interface.addresses[0] for _node in cluster.nodes])
    node_roles = " ".join(node.roles)
    env_file_content = f"""# Node configuration properties
APPLICATION_VERSION={cluster.application.version}
NODE_IPS=({node_ips})
ROLES=({node_roles})
"""
    node.instance.addService(pg.Execute(shell="bash", command=f"echo \"{env_file_content}\" > node_configuration.sh"))
    node.instance.addService(pg.Execute(shell="bash", command="install.sh"))

def nodeDetermineRolesCassandra(nodes: list[Node]) -> None:
    # TODO: Implement this
    pass

def nodeDetermineRolesMongoDB(nodes: list[Node]) -> None:
    # TODO: Implement this
    pass

def nodeDetermineRolesScylla(nodes: list[Node]) -> None:
    # TODO: Implement this
    pass

def nodeDetermineRolesElasticsearch(nodes: list[Node]) -> None:
    # TODO: Implement this
    pass

def provisionLAN(request: pg.Request, params: portal.Namespace, cluster: Cluster) -> None:
    lan: pg.LAN = pg.LAN("LAN")
    for node in cluster.nodes:
        lan.addInterface(node.interface)
    lan.connectSharedVlan(params.vlan_type)
    request.addResource(lan)

def bootstrapDB(request: pg.Request, params: portal.Namespace) -> Cluster:
    cluster: Cluster = Cluster(Application(
        params.cluster_application,
        params.cluster_application_version
    ))
    for i in range(params.node_count):
        cluster.nodes.append(nodeProvision(i, request, params))
    if cluster.application.variant == ApplicationVariant.CASSANDRA:
        nodeDetermineRolesCassandra(cluster.nodes)
    elif cluster.application.variant == ApplicationVariant.MONGO_DB:
        nodeDetermineRolesMongoDB(cluster.nodes)
    elif cluster.application.variant == ApplicationVariant.SCYLLA:
        nodeDetermineRolesScylla(cluster.nodes)
    elif cluster.application.variant == ApplicationVariant.ELASTICSEARCH:
        nodeDetermineRolesElasticsearch(cluster.nodes)
    # Addresses are assigned in previous loop, we need to know
    # them all before installing as each node should know the
    # addresses of all other nodes
    for node in cluster.nodes:
        nodeInstallApplication(cluster, node)
    
    provisionLAN(request, params, cluster)
    return cluster

# === CORE === #

def validateParameters(params: portal.Namespace) -> None:
    if params.node_count < 1 or params.node_count > 3:
        portal.context.reportError(portal.ParameterError("Node count must be in range [1,3]", ["node_count"]))
    portal.context.verifyParameters()

def main() -> None:
    portal.context.defineParameterGroup(PARAMETER_GROUP_CLUSTER, "Cluster")
    portal.context.defineParameterGroup(PARAMETER_GROUP_NODE, "Node")
    portal.context.defineParameter("node_count", "Number of DB nodes", portal.ParameterType.INTEGER, 1, groupId=PARAMETER_GROUP_NODE)
    portal.context.defineParameter("node_size", "Instance size for each node", portal.ParameterType.STRING, "<TODO>", groupId=PARAMETER_GROUP_NODE)
    portal.context.defineParameter("node_disk_image", "Node disk image", portal.ParameterType.STRING, "<TODO>", groupId=PARAMETER_GROUP_NODE)
    portal.context.defineParameter(
        "vlan_type",
        "VLAN Type",
        portal.ParameterType.STRING,
        "mesoscale-openflow",
        [
            # ('mlnx-sn2410', 'Mellanox SN2410'),
            # ('dell-s4048',  'Dell S4048'),
            ("mesoscale-openflow", "Mesoscale OpenFlow")
        ],
        groupId=PARAMETER_GROUP_CLUSTER
    )
    portal.context.defineParameter(
        "cluster_application",
        "Cluster Application",
        portal.ParameterType.STRING,
        ApplicationVariant.CASSANDRA,
        [(app, str(app).title()) for app in ApplicationVariant],
        groupId=PARAMETER_GROUP_CLUSTER
    )
    portal.context.defineParameter(
        "cluster_application_version",
        "Cluster application version",
        portal,portal.ParameterType.STRING,
        groupId=PARAMETER_GROUP_CLUSTER
    )
    params: portal.Namespace = portal.context.bindParameters()
    request: pg.Request = portal.context.makeRequestRSpec()
    validateParameters(params)
    cluster: Cluster = bootstrapDB(request, params)
    bootstrapCollector(request, params, cluster)
    portal.context.printRequestRSpec()
    
