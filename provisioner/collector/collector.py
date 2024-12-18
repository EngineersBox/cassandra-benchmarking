from dataclasses import dataclass

from geni import portal
from provisioner.parameters import Parameter, ParameterGroup
from provisioner.structure.node import Node

@dataclass
class Collector:
    node: Node

class CollectorParameterGroup(ParameterGroup):

    @classmethod
    def name(cls) -> str:
        return "Collector"

    @classmethod
    def id(cls) -> str:
        return "collector"

    def __init__(self):
        super().__init__(
            parameters=[
                Parameter(
                    name="collector_version",
                    description="Version of the OTEL collector",
                    typ=portal.ParameterType.STRING,
                    required=True
                ),
                Parameter(
                    name="ycsb_version",
                    description="Version of the YCSB benchmarking suite",
                    typ=portal.ParameterType.STRING,
                    defaultValue="0.17.0"
                )
            ]
        )

    def validate(self, params: portal.Namespace) -> None:
        super().validate(params)

COLLECTOR_PARAMETERS: ParameterGroup = CollectorParameterGroup()
