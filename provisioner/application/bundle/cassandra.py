import math
from typing import Any, Optional, Tuple
from geni.rspec import pg
import geni.portal as portal

from provisioner.application.datacentre import DataCentre
from ..app import AbstractApplication, ApplicationVariant, LOCAL_PATH
from ..node import Node
from ..rack import Rack
from ..cluster import Cluster

CASSANDRA_YAML_DEFAULT_PROPERTIES: dict[str, Any] = {
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

class CassandraApplication(AbstractApplication):
    all_ips: list[pg.Interface] = []
    # Node Ids to node interfaces
    seeds: dict[str, pg.Interface] = {}
    topology: dict[Node, Tuple[DataCentre, Rack]] = {}

    def __init__(self, version: str):
        super().__init__(version)

    @classmethod
    def variant(cls) -> ApplicationVariant:
        return ApplicationVariant.CASSANDRA

    def preConfigureClusterLevelProperties(self, cluster: Cluster, params: portal.Namespace) -> None:
        super().preConfigureClusterLevelProperties(cluster, params)
        self.cluster = cluster
        self.determineSeedNodes(cluster, params)
        self.constructTopology(cluster)
        # TODO: Cluster level properties

    def determineSeedNodes(self, cluster: Cluster, params: portal.Namespace) -> None:
        # Spread seeds across DCs to ensure at least 1 per DC.
        # Seeds within DCs should be spread across racks too.
        self.all_ips = [node.interface for node in cluster.nodesGenerator()]
        nodes_per_dc: int = params.racks_per_dc * params.nodes_per_rack
        seeds_per_dc: int = int(math.log2(nodes_per_dc))
        for dc in cluster.datacentres.values():
            racks: list[Rack] = list(dc.racks.values())
            for i in range(seeds_per_dc):
                rack: Rack = racks[i % len(racks)]
                for node in rack.nodes:
                    if (node.id in self.seeds):
                        continue
                    self.seeds[node.id] = node.interface
                    break

    def constructTopology(self, cluster: Cluster) -> None:
        for dc in cluster.datacentres.values():
            for rack in dc.racks.values():
                for node in rack.nodes:
                    self.topology[node] = (dc, rack)

    def writeRackDcProperties(self, node: Node) -> None:
        dc, rack = self.topology[node]
        properties = f"""# DC and Rack specification of this node
dc={dc.name}
rack={rack.name}
"""
        node.instance.addService(pg.Execute(
            shell="bash",
            command=f"echo \"{properties}\" > {LOCAL_PATH}/config/cassandra-rackdc.properties"
        ))

    def writeTopologyProperties(self, node: Node) -> None:
        default_dc, default_rack = list(self.topology.values())[0]
        properties = f"""# Mappings of Node IP=DC:Rack
# Default mapping for unknown nodes
default={default_dc.name}:{default_rack.name}
"""
        for node, (dc, rack) in self.topology.items():
            properties.join(f"\n{node.interface.addresses[0].address}={dc.name}:{rack.name}")
        node.instance.addService(pg.Execute(
            shell="bash",
            command=f"echo \"{properties}\" > {LOCAL_PATH}/config/cassandra-topology.properties"
        ))

    def nodeInstallApplication(self, node: Node) -> None:
        super().nodeInstallApplication(node)
        self._unpackApplication(
            node,
            f"https://github.com/EngineersBox/cassandra-benchmarking/releases/{super().version}/{CassandraApplication.variant()}.tar.gz"
        )
        all_ips_prop: str = " ".join([f"\"{iface.addresses[0]}\"" for iface in self.all_ips])
        self._invokeInstaller(
            node,
            {
                "NODE_ALL_IPS": "({})".format(all_ips_prop),
                "SEED_NODE": "true" if node in self.seeds else "false"
            }
        )
        self.writeRackDcProperties(node)
        self.writeTopologyProperties(node)
