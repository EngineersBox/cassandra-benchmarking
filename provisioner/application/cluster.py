from dataclasses import dataclass
from .datacentre import DataCentre
from ..parameters import Parameter, ParameterGroup
import geni.portal as portal

@dataclass
class Cluster:
    datacentres: dict[str, DataCentre]

CLUSTER_PARAMETER_GROUP = "Cluster"
CLUSTER_PARAMETERS: ParameterGroup = ParameterGroup(
    name=CLUSTER_PARAMETER_GROUP,
    parameters=[
        Parameter(
            name="datacentre_count",
            description="Number of datacentres",
            typ=portal.ParameterType.INTEGER,
            defaultValue=1
        ),
        Parameter(
            name="rack_count",
            description="Number of racks in each datacentre",
            typ=portal.ParameterType.INTEGER,
            defaultValue=1
        ),
        Parameter(
            name="node_count",
            description="Number of nodes in each rack",
            typ=portal.ParameterType.INTEGER,
            defaultValue=1
        )
    ]
)
