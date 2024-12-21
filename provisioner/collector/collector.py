from dataclasses import dataclass
from enum import Enum
import itertools, re
from typing import Optional, Tuple
from geni import portal
from provisioner.parameters import Parameter, ParameterGroup
from provisioner.structure.node import Node

@dataclass
class Collector:
    node: Node

class OTELFeature(Enum):
    METRICS = "metrics"
    LOGS = "logs"
    TRACES = "traces"

    def __str__(self) -> str:
        return "%s" % self.value

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
                ),
                Parameter(
                    name="collector_features",
                    description="Comma separated features to enable with OTEL integration. It can be any combination of [metrics, logs, traces]",
                    typ=portal.ParameterType.STRING,
                    defaultValue="metrics,logs,traces"
                )
            ]
        )

    def validate(self, params: portal.Namespace) -> None:
        super().validate(params)
        features: str = params.collector_features
        pattern: re.Pattern = re.compile("\\s+")
        features = pattern.sub(" ", features).upper()
        split_features: list[str] = features.split(",")
        new_features: set[OTELFeature] = set([])
        for feat in split_features:
            otel_feature: OTELFeature
            try:
                otel_feature = OTELFeature[feat]
            except KeyError:
                valid_features = ",".join(OTELFeature._member_map_.keys())
                portal.context.reportError(portal.ParameterError(
                    f"Invalid collector feature {feat}, must be one of [{valid_features}]",
                    ["collector_features"]
                ))
                continue
            if otel_feature in new_features:
                portal.context.reportError(portal.ParameterError(
                    f"Duplicated collector feature {feat}",
                    ["collector_features"]
                ))
                continue
            new_features.add(otel_feature)
        params.collector_features = new_features

COLLECTOR_PARAMETERS: ParameterGroup = CollectorParameterGroup()
