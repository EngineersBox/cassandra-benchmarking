from ..app import AbstractApplication, ApplicationVariant
from ..node import Node


class ElasticsearchApplication(AbstractApplication):

    def __init__(self, version: str):
        super().__init__(ApplicationVariant.ELASTICSEARCH, version)

    def nodeDetermineRoles(self, nodes: list[Node]) -> None:
        super().nodeDetermineRoles(nodes)
        # TODO: Implement this
