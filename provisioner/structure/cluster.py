import geni.portal as portal
from dataclasses import dataclass, field
from typing import Iterator
from provisioner.structure.node import Node
from provisioner.structure.rack import Rack
from provisioner.structure.datacentre import DataCentre
from provisioner.parameters import Parameter, ParameterGroup

@dataclass
class Cluster:
    datacentres: dict[str, DataCentre] = field(default_factory=dict)

    def racksGenerator(self) -> Iterator[Rack]:
        for dc in self.datacentres.values():
            for rack in dc.racks.values():
                yield rack

    def nodesGenerator(self) -> Iterator[Node]:
        for rack in self.racksGenerator():
            for node in rack.nodes:
                yield node

class ClusterParameterGroup(ParameterGroup):

    @classmethod
    def name(cls) -> str:
        return "Cluster"

    @classmethod
    def id(cls) -> str:
        return "cluster"

    def __init__(self):
        super().__init__(
            parameters=[
                Parameter(
                    name="dc_count",
                    description="Number of datacentres",
                    typ=portal.ParameterType.INTEGER,
                    defaultValue=1
                ),
                Parameter(
                    name="racks_per_dc",
                    description="Number of racks in each datacentre",
                    typ=portal.ParameterType.INTEGER,
                    defaultValue=1
                ),
                Parameter(
                    name="nodes_per_rack",
                    description="Number of nodes in each rack",
                    typ=portal.ParameterType.INTEGER,
                    defaultValue=1
                ),
                Parameter(
                    name="node_size",
                    description="Instance to use for the nodes",
                    typ=portal.ParameterType.STRING,
                    defaultValue="<TODO>"
                ),
                Parameter(
                    name="node_disk_image",
                    description="Node disk image",
                    typ=portal.ParameterType.STRING,
                    defaultValue="<TODO>"
                ),
                Parameter(
                    name="vlan_type",
                    description="VLAN to use when connecting nodes",
                    typ=portal.ParameterType.STRING,
                    defaultValue="mesoscale-openflow",
                    legalValues=[
                        # ('mlnx-sn2410', 'Mellanox SN2410'),
                        # ('dell-s4048',  'Dell S4048'),
                        ("mesoscale-openflow", "Mesoscale OpenFlow")
                    ]
                )
            ]
        )

    def validate(self,params: portal.Namespace) -> None:
        super().validate(params)
        total_nodes = params.dc_count * params.racks_per_dc * params.nodes_per_rack
        if total_nodes < 1 or total_nodes > 9:
            portal.context.reportError(portal.ParameterError(
                "Node count must be in range [1,9]",
                ["node_count"]
            ))

CLUSTER_PARAMETERS: ParameterGroup = ClusterParameterGroup()
