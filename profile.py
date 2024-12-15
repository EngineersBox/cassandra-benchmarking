import geni.portal as portal
import geni.rspec.pg as pg 
from provisioner.application.cluster import CLUSTER_PARAMETERS, Cluster
from provisioner.application.app import APPLICATION_PARAMETERS
from provisioner.provisoner import Provisioner

def validateParameters(params: portal.Namespace) -> None:
    if params.node_count < 1 or params.node_count > 9:
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
    portal.context.printRequestRSpec()

if __name__ == "__main__":
    main()
