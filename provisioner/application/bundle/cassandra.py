from typing import Any
from dataclasses import dataclass
from geni.rspec import pg
from ..app import AbstractApplication, ApplicationVariant
from ..node import Node
from ..cluster import Cluster

DEFAULT_CASSANDRA_YAML: dict[str, Any] = {
    "cluster_name": "Cassandra Cluster",
    "num_tokens": 16,
    "prepared_statements_cache_size": "",
    "row_cache_size": "0MiB",
    "row_cache_save_period": "0s",
    "commit_log_segment_size": "32MiB",
    "commit_log_disk_access_mode": "auto",
    "commit_log_total_space": "8192MiB",
    "seed_node_ips": "",
    "concurrent_reads": 32,
    "concurrent_writes": 32,
    "concurrent_counter_writes": 32,
    "networking_cache_size": "128MiB",
    "file_cache_enabled": "false",
    "file_cache_size": "512MiB",
    "buffer_pool_use_heap_if_exhausted": "false",
    "memtable_heap_space": "",
    "memtable_offheap_space": "",
    "memtable_allocation_type": "heap_buffers",
    "memtable_flush_writers": 2,
    "trickle_fsync": "false",
    "trickle_fsync_interval": "10240KiB",
    "listen_address": "127.0.0.1",
    "boradcast_address": "127.0.0.1",
    "rpc_address": "0.0.0.0",
    "broadcast_rpc_address": "127.0.0.1",
    "sstable_scaling_parameters": "T4",
    "sstable_target_size": "1GiB",
    "concurrent_compactors": 16,
    "compaction_throughput": "64MiB/s",
    "sstable_preemptive_open_interval": "50MiB",
    "endpoint_snitch": "GossipingPropertyFileSnitch",
    "internode_compression": "dc",
    "internode_dc_tcp_nodelay": "false"
}

@dataclass
class Rack:
    name: str
    nodes: list[Node]

@dataclass
class DataCentre:
    name: str
    racks: list[Rack]


class CassandraApplication(AbstractApplication):
    all_ips: list[pg.Interface] = []
    seeds: list[pg.Interface] = []

    def __init__(self, version: str):
        super().__init__(ApplicationVariant.CASSANDRA, version)

    def preConfigureClusterLevelProperties(self, cluster: Cluster) -> None:
        super().preConfigureClusterLevelProperties(cluster)
        self.determineSeedNodes(cluster.nodes)
        # TODO: Cluster level properties

    def determineSeedNodes(self, nodes: list[Node]) -> None:
        self.all_ips = [node.interface for node in nodes]
        self.seeds = self.all_ips[:int((len(nodes) / 2) + 1)]

    def 

    def nodeInstallApplication(self, node: Node) -> None:
        super().nodeInstallApplication(node)
        node.instance.addService(pg.Install(
            # TODO: Make sure this URL is correct and constructed properly
            url=f"https://github.com/EngineersBox/cassandra-benchmarking/releases/{super().version}/{super().variant}.tar.gz",
            path="/local"
        ))
        # Bash env file
        node_ips = " ".join([addr.addresses[0] for addr in self.all_ips])
        env_file_content = f"""# Node configuration properties
APPLICATION_VARIANT={super().variant}
APPLICATION_VERSION={super().version}
NODE_IPS=({node_ips})
"""
        node.instance.addService(pg.Execute(shell="bash", command=f"echo \"{env_file_content}\" > node_configuration.sh"))
        node.instance.addService(pg.Execute(shell="bash", command="install.sh"))
        # Cassandra configuration
        # TODO: 1. Read from template YAML config
        #       2. Replace template entries with values
        #       3. Write to node as service
        cass_yaml_content = ""
        node.instance.addService(pg.Execute(shell="bash", command=f"echo \"{cass_yaml_content}\" > /local/config/cassandra/cassandra.yaml"))
