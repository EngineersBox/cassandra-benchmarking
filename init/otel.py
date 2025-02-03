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
    session = None
    # Get a connection
    while (True):
        try:
            logging.info("Connecting to Cassandra cluster")
            cluster = Cluster(contact_points=[f"{node_ips[0]}:9042"])
            session = cluster.connect()
            break
        except:
            logging.warning("Attempt failed, sleeping for %d seconds", CONNECT_RETRY_DELAY_SECONDS)
            time.sleep(CONNECT_RETRY_DELAY_SECONDS)
    
    logging.info("Established connection to Cassandra cluster")
    # Wait for all nodes to come up
    while (len(node_ips) == 0):
        # Query all peers and their state
        result_set: ResultSet = session.execute("select * from system.peers_v2;")
        rows = result_set.all()
        # Remove the peers that are up from the list of node_ips we have
        for row in rows:
            # FIXME:: Replace these template strings with whatever the real ones are
            if (row["<STATE COLUMN NAME>"] == "UP" and row["<NODE_IP_COLUMN>"] in node_ips):
                node_ips.remove(row["<NODE_IP_COLUMN>"])
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
