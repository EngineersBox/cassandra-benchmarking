import geni.portal as portal
import geni.rspec.pg as pg 
from provisioner.application.cluster import CLUSTER_PARAMETERS, Cluster
from provisioner.application.app import APPLICATION_PARAMETERS
from provisioner.provisoner import Provisioner

DEBUG_OUTPUT = True

def validateParameters(params: portal.Namespace) -> None:
    CLUSTER_PARAMETERS.validate(params)
    APPLICATION_PARAMETERS.validate(params)
    total_nodes = params.dc_count * params.racks_per_dc * params.nodes_per_rack
    if total_nodes < 1 or total_nodes > 9:
        portal.context.reportError(portal.ParameterError("Node count must be in range [1,9]", ["node_count"]))
    portal.context.verifyParameters()

def main() -> None:
    CLUSTER_PARAMETERS.bind()
    APPLICATION_PARAMETERS.bind()
    params: portal.Namespace = portal.context.bindParameters()
    request: pg.Request = portal.context.makeRequestRSpec()
    validateParameters(params)
    provisioner: Provisioner = Provisioner()
    cluster: Cluster = provisioner.bootstrapDB(request, params)
    provisioner.bootstrapCollector(request, params, cluster)
    if DEBUG_OUTPUT:
        request.writeXML("./test.xml")
    else:
        portal.context.printRequestRSpec()

if __name__ == "__main__":
    main()
