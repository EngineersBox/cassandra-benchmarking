from enum import Enum
import os, time, logging
from typing import Callable, Optional
from cassandra.cluster import Cluster, Host

logging.basicConfig(format="[%(levelname)s] %(name)s :: %(message)s", level=logging.DEBUG)


CONNECT_RETRY_DELAY_SECONDS = 5

def filterUpHosts(hosts: list[Host]) -> list[Host]:
    return list(filter(lambda host: host.is_up, hosts))

def checkHosts(node_ips: list[str], contact_points: list[str]) -> bool:
    cluster: Optional[Cluster] = None
    try:
        logging.info("Connecting to Cassandra cluster")
        # Get a connection
        cluster = Cluster(contact_points=contact_points)
        cluster.connect()
        logging.info("Established connection to Cassandra cluster")
    except:
        logging.warning("Connection failed, retrying")
        if (cluster != None):
            cluster.shutdown()
        return False
    if cluster.metadata == None:
        cluster.shutdown()
        return False;
    # Retrieve all cluster nodes (hosts)
    hosts = cluster.metadata.all_hosts()
    if len(hosts) != node_ips:
        logging.info(f"Retrieved {len(hosts)} hosts, but have {len(node_ips)} IPs, retrying")
        cluster.shutdown()
        return False
    # Wait for all nodes to come up
    up_hosts = filterUpHosts(hosts)
    if (len(up_hosts) == len(node_ips)):
        cluster.shutdown()
        return True
    logging.info(f"{len(up_hosts)}/{len(node_ips)} nodes are up")
    cluster.shutdown()
    return False

def mainCassandra() -> None:
    node_ips = os.environ["CASSANDRA_NODE_IPS"].split(",")
    contact_points = node_ips[:min(len(node_ips), 3)]
    while (not checkHosts(node_ips, contact_points)):
        time.sleep(CONNECT_RETRY_DELAY_SECONDS)
    # Sleep for a minute for good measure
    time.sleep(60)
    pass

def mainMongoDB() -> None:
    pass

def mainScylla() -> None:
    pass

def mainElasticsearch() -> None:
    pass

class ApplicationVariant(Enum):
    CASSANDRA = mainCassandra
    MONGO_DB = mainMongoDB
    SCYLLA = mainScylla
    ELASTICSEARCH = mainElasticsearch
    OTEL_COLLECTOR = None

    def isProvisionable(self) -> bool:
        return self.value != None

    def mainMethod(self) -> Callable[[], None]:
        if (self.value == None):
            raise ValueError(f"Variant is non-provisionable: {self.name}")
        return self.value

def main() -> None:
    env_cluster_application_variant = os.environ["CLUSTER_APPLICATION_VARIANT"].upper()
    if (env_cluster_application_variant not in ApplicationVariant._member_names_):
        raise RuntimeError(f"Unknown variant specified in CLUSTER_APPLICATION_VARIANT env var: {env_cluster_application_variant}")
    app_variant: ApplicationVariant = ApplicationVariant(ApplicationVariant._member_map_[env_cluster_application_variant])
    if (not app_variant.isProvisionable()):
        raise ValueError(f"CLUSTER_APPLICATION_VARIANT is {env_cluster_application_variant} which is not provisionable and thus cannot be interfaced with")
    callable: Callable[[], None] = app_variant.mainMethod()
    callable()

if __name__ == "__main__":
    main()
