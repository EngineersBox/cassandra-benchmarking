from enum import Enum
import os, time, random, logging
from cassandra.cluster import Cluster, ResultSet

logging.basicConfig(format="[%(levelname)s] %(name)s :: %(message)s", level=logging.DEBUG)

class ApplicationVariant(Enum):
    CASSANDRA = "cassandra", True
    MONGO_DB = "mongodb", True
    SCYLLA = "scylla", True
    ELASTICSEARCH = "elasticsearch", True,
    OTEL_COLLECTOR = "otel_collector", False

CONNECT_RETRY_DELAY_SECONDS = 5

def mainCassandra() -> None:
    node_ips = os.environ["CASSANDRA_NODE_IPS"].split(",")
    # Pop the node because once we connect to the cluster, everything is
    # ok on that node (in terms of conditions for the rest of OTEL init)
    # and also because the system.peers_v2 table does not contain the
    # current node you are connected to.
    target_node = node_ips.pop(0)
    session = None
    # Get a connection
    while (True):
        try:
            logging.info("Connecting to Cassandra cluster")
            cluster = Cluster(contact_points=[f"{target_node}:9042"])
            session = cluster.connect()
            break
        except:
            logging.warning("Attempt failed, sleeping for %d seconds", CONNECT_RETRY_DELAY_SECONDS)
            time.sleep(CONNECT_RETRY_DELAY_SECONDS)
    
    logging.info("Established connection to Cassandra cluster")
    # Wait for all nodes to come up
    while (len(node_ips) == 0):
        # Query all peers and their state
        result_set: ResultSet = session.execute("select peer from system.peers_v2;")
        rows = result_set.all()
        # Remove the peers that are up from the list of node_ips we have
        for row in rows:
            # FIXME: The system.peers_v2 table doesn't have the state of the
            #        nodes. Maybe it is easier to just connect to each node,
            #        pull the system.local table and look at the boostrapped
            #        column to see if it is 'COMPLETED' to determine if the
            #        node is up or not.
            if (row["peer"] in node_ips):
                node_ips.remove(row["peer"])
    # Sleep for a minute for good measure
    time.sleep(60)
    pass

def mainMongoDB() -> None:
    pass

def mainScylla() -> None:
    pass

def mainElasticsearch() -> None:
    pass

def main() -> None:
    env_cluster_application_variant = os.environ["CLUSTER_APPLICATION_VARIANT"].upper()
    if (env_cluster_application_variant not in ApplicationVariant._member_names_):
        raise RuntimeError(f"Unknown variant specified in CLUSTER_APPLICATION_VARIANT env var: {env_cluster_application_variant}")
    app_variant: ApplicationVariant = ApplicationVariant(ApplicationVariant._member_map_[env_cluster_application_variant])
    if (app_variant == ApplicationVariant.CASSANDRA):
        mainCassandra()
    elif (app_variant == ApplicationVariant.MONGO_DB):
        mainMongoDB()
    elif (app_variant == ApplicationVariant.SCYLLA):
        mainScylla()
    elif (app_variant == ApplicationVariant.ELASTICSEARCH):
        mainElasticsearch()
    elif (app_variant == ApplicationVariant.OTEL_COLLECTOR):
        raise RuntimeError("CLUSTER_APPLICATION_VARIANT cannot be OTEL_COLLECTOR")

if __name__ == "__main__":
    main()
