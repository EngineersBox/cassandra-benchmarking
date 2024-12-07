from ..app import AbstractApplication, ApplicationVariant
from ..node import Node


class MongoDBApplication(AbstractApplication):

    def __init__(self, version: str):
        super().__init__(ApplicationVariant.MONGO_DB, version)

    def nodeDetermineRoles(self, nodes: list[Node]) -> None:
        super().nodeDetermineRoles(nodes)
        # TODO: Implement this
