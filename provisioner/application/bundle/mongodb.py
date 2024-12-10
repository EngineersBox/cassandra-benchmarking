from ..app import AbstractApplication, ApplicationVariant
from ..node import Node
from ..cluster import Cluster


class MongoDBApplication(AbstractApplication):

    def __init__(self, version: str):
        super().__init__(version)

    @classmethod
    def variant(cls) -> ApplicationVariant:
        return ApplicationVariant.MONGO_DB

    def preConfigureClusterLevelProperties(self, cluster: Cluster) -> None:
        # TODO: Implement this
        pass

    def nodeInstallApplication(self, node: Node) -> None:
        # TODO: Implement this
        pass
