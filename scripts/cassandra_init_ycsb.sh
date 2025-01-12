#!/usr/bin/env bash

read -r -d '' CQL_SCRIPT << EOM
create keyspace ycsb with replication = {'class' : 'SimpleStrategy', 'replication_factor': 1 };
create table ycsb.usertable (
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
) with compaction = {'class': 'LeveledCompactionStrategy'} and memtable = 'trie';
EOM

# CQLSH_PYTHON="$(which python3.6)" ~/repos/cassandra/bin/cqlsh -e "$CQL_SCRIPT}"
docker exec cassandra /var/lib/cassandra/bin/cqlsh -e "$CQL_SCRIPT"
