from dataclasses import dataclass
from typing import Generator, Iterable

from .node import Node
from .rack import Rack
from .datacentre import DataCentre
from ..parameters import Parameter, ParameterGroup
import geni.portal as portal

@dataclass
class Cluster:
    datacentres: dict[str, DataCentre] = {}

    def racksGenerator(self) -> Generator[Rack]:
        for dc in self.datacentres.values():
            for rack in dc.racks.values():
                yield rack

    def nodesGenerator(self) -> Generator[Node]:
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

    def validate(self) -> None:
        super().validate()

CLUSTER_PARAMETERS: ParameterGroup = ClusterParameterGroup()
