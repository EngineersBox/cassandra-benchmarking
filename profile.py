import geni.portal as portal
import geni.rspec.pg as pg 
from .provisioner.application.cluster import Cluster
from .provisioner.application.app import ApplicationVariant
from .provisioner.provisoner import Provisioner

PARAMETER_GROUP_CLUSTER = "cluster"
PARAMETER_GROUP_NODE = "node"

def validateParameters(params: portal.Namespace) -> None:
    if params.node_count < 1 or params.node_count > 9:
        portal.context.reportError(portal.ParameterError("Node count must be in range [1,9]", ["node_count"]))
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
    provisioner: Provisioner = Provisioner()
    cluster: Cluster = provisioner.bootstrapDB(request, params)
    provisioner.bootstrapCollector(request, params, cluster)
    portal.context.printRequestRSpec()
    
