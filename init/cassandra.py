import os
from cassandra.cluster import Cluster

def constructReplication() -> str:
    rf = ""
    for i in range(int(os.environ["DC_COUNT"])):
        rf += f"\t'dc-{i}': {os.environ['YCSB_RF']},\n"
    return rf.removesuffix(",\n").removeprefix("\t")

def main() -> None:
    cluster = Cluster(contact_points=[os.environ["NODE_IP"]])
    session = cluster.connect()
    session.execute(f"""create keyspace ycsb with replication = {{
        'class': 'NetworkTopologyStrategy',
        {constructReplication()}, 
    }} with compaction {{
        'class': 'UnifiedCompactionStrategy'
    }} and memtable = 'trie';""")
    session.execute("""create table ycsb.usertable (
        y_id varchar primary key,
        field0 varchar,
        field1 varchar,
        field2 varchar,
        field3 varchar,
        field4 varchar,
        field5 varchar,
        field6 varchar,
        field7 varchar,
        field8 varchar,
        field9 varchar
    ) with compaction = {'class': 'UnifiedCompactionStrategy'}
    and memtable = 'trie';""")

if __name__ == "__main__":
    main()
