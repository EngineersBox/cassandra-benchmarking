/* =============================
 *          CASSANDRA
 * =============================
 */

def __instrumentCassandra() {
    def cassandraMetrics = "org.apache.cassandra.metrics"
    def clientRequest = "${cassandraMetrics}:type=ClientRequest"
    def clientRequestRangeSlice = "${clientRequest},scope=RangeSlice"

    def clientRequestRangeSliceLatency = otel.mbean("${clientRequestRangeSlice},name=Latency")
    otel.instrument(clientRequestRangeSliceLatency,
            "cassandra.client.request.range_slice.latency.50p",
            "Token range read request latency - 50th percentile", "us", "50thPercentile",
            otel.&doubleValueCallback)

    otel.instrument(clientRequestRangeSliceLatency,
            "cassandra.client.request.range_slice.latency.99p",
            "Token range read request latency - 99th percentile", "us", "99thPercentile",
            otel.&doubleValueCallback)

    otel.instrument(clientRequestRangeSliceLatency,
            "cassandra.client.request.range_slice.latency.max",
            "Maximum token range read request latency", "us", "Max",
            otel.&doubleValueCallback)

    def clientRequestRead = "${clientRequest},scope=Read"
    def clientRequestReadLatency = otel.mbean("${clientRequestRead},name=Latency")
    otel.instrument(clientRequestReadLatency,
            "cassandra.client.request.read.latency.50p",
            "Standard read request latency - 50th percentile", "us", "50thPercentile",
            otel.&doubleValueCallback)

    otel.instrument(clientRequestReadLatency,
            "cassandra.client.request.read.latency.99p",
            "Standard read request latency - 99th percentile", "us", "99thPercentile",
            otel.&doubleValueCallback)

    otel.instrument(clientRequestReadLatency,
            "cassandra.client.request.read.latency.max",
            "Maximum standard read request latency", "us", "Max",
            otel.&doubleValueCallback)

    def clientRequestWrite = "${clientRequest},scope=Write"
    def clientRequestWriteLatency = otel.mbean("${clientRequestWrite},name=Latency")
    otel.instrument(clientRequestWriteLatency,
            "cassandra.client.request.write.latency.50p",
            "Regular write request latency - 50th percentile", "us", "50thPercentile",
            otel.&doubleValueCallback)

    otel.instrument(clientRequestWriteLatency,
            "cassandra.client.request.write.latency.99p",
            "Regular write request latency - 99th percentile", "us", "99thPercentile",
            otel.&doubleValueCallback)

    otel.instrument(clientRequestWriteLatency,
            "cassandra.client.request.write.latency.max",
            "Maximum regular write request latency", "us", "Max",
            otel.&doubleValueCallback)

    def storage = "${cassandraMetrics}:type=Storage"
    def storageLoad = otel.mbean("${storage},name=Load")
    otel.instrument(storageLoad,
            "cassandra.storage.load.count",
            "Size of the on disk data size this node manages", "by", "Count",
            otel.&longUpDownCounterCallback)

    def storageTotalHints = otel.mbean("${storage},name=TotalHints")
    otel.instrument(storageTotalHints,
            "cassandra.storage.total_hints.count",
            "Number of hint messages written to this node since [re]start", "1", "Count",
            otel.&longCounterCallback)

    def storageTotalHintsInProgress = otel.mbean("${storage},name=TotalHintsInProgress")
    otel.instrument(storageTotalHintsInProgress,
            "cassandra.storage.total_hints.in_progress.count",
            "Number of hints attempting to be sent currently", "1", "Count",
            otel.&longUpDownCounterCallback)


    def compaction = "${cassandraMetrics}:type=Compaction"
    def compactionPendingTasks = otel.mbean("${compaction},name=PendingTasks")
    otel.instrument(compactionPendingTasks,
            "cassandra.compaction.tasks.pending",
            "Estimated number of compactions remaining to perform", "1", "Value",
            otel.&longValueCallback)

    def compactionCompletedTasks = otel.mbean("${compaction},name=CompletedTasks")
    otel.instrument(compactionCompletedTasks,
            "cassandra.compaction.tasks.completed",
            "Number of completed compactions since server [re]start", "1", "Value",
            otel.&longCounterCallback)


    def clientRequests = otel.mbeans([
      "${clientRequestRangeSlice},name=Latency",
      "${clientRequestRead},name=Latency",
      "${clientRequestWrite},name=Latency",
    ])

    otel.instrument(clientRequests,
      "cassandra.client.request.count",
      "Number of requests by operation",
      "1",
      [
        "operation" : { mbean -> mbean.name().getKeyProperty("scope") },
      ],
      "Count", otel.&longCounterCallback)

    def clientRequestErrors = otel.mbeans([
      "${clientRequestRangeSlice},name=Unavailables",
      "${clientRequestRangeSlice},name=Timeouts",
      "${clientRequestRangeSlice},name=Failures",
      "${clientRequestRead},name=Unavailables",
      "${clientRequestRead},name=Timeouts",
      "${clientRequestRead},name=Failures",
      "${clientRequestWrite},name=Unavailables",
      "${clientRequestWrite},name=Timeouts",
      "${clientRequestWrite},name=Failures",
    ])

    otel.instrument(clientRequestErrors,
      "cassandra.client.request.error.count",
      "Number of request errors by operation",
      "1",
      [
        "operation" : { mbean -> mbean.name().getKeyProperty("scope") },
        "status" : {
          mbean -> switch(mbean.name().getKeyProperty("name")) {
            case "Unavailables":
              return "Unavailable"
              break
            case "Timeouts":
              return "Timeout"
              break
            case "Failures":
              return "Failure"
              break
          }
        }
      ],
      "Count", otel.&longCounterCallback
    )

    def serializerMetrics = [
        "Cell",
        "Cfs",
        "ClusteringKey",
        "Column",
        "ColumnSubset",
        "IndexEntry",
        "RangeTombstoneMarker",
        "RowBody",
        "Row"
    ]
    def serializerTypePrefixes = [
        "Partition",
        "Index",
        "Data",
        "SSTableWriter"
    ]
    def serializerMBeanAttributes = [
        "50thPercentile": otel.&doubleCounterCallback,
        "75thPercentile": otel.&doubleCounterCallback,
        "95thPercentile": otel.&doubleCounterCallback,
        "98thPercentile": otel.&doubleCounterCallback,
        "99thPercentile": otel.&doubleCounterCallback,
        "999thPercentile": otel.&doubleCounterCallback,
        "Count": otel.&longCounterCallback,
        "OneMinuteRate": otel.&doubleCounterCallback,
        "FifteenMinuteRate": otel.&doubleCounterCallback,
        "FiveMinuteRate": otel.&doubleCounterCallback,
        "OneMinuteRate": otel.&doubleCounterCallback,
        "OneMinuteRate": otel.&doubleCounterCallback,
        "Max": otel.&doubleCounterCallback,
        "Mean": otel.&doubleCounterCallback,
        "MeanRate": otel.&doubleCounterCallback,
        "Min": otel.&doubleCounterCallback,
        // "RecentValues": otel.&longHistogram,
        "StdDev": otel.&doubleCounterCallback,
    ]
    serializerTypePrefixes.each { prefix ->
        serializerMetrics.each { metric ->
            serializerMBeanAttributes.each { attribute, func ->
                def name = "${prefix}${metric}"
                def serializer = otel.mbean(
                    "org.apache.cassandra.metrics:name=${name}SerializerRate,*",
                )
                otel.instrument(
                    serializer,
                    "cassandra.serializer.${prefix.toLowerCase()}.${metric.toLowerCase()}.${attribute.toLowerCase()}",
                    "<todo description>",
                    "1",
                    [
                        "type": { mbean -> mbean.name().getKeyProperty("type") },
                        "keyspace": { mbean -> mbean.name().getKeyProperty("keyspace") },
                        "scope": { mbean -> mbean.name().getKeyProperty("scope") },
                    ],
                    [ "${attribute}": [ "${attribute}": "${attribute}" ] ],
                    func
                )
            }
        }
    }
}

/* =============================
 *             JVM
 * =============================
 */

def __instrumentJVM() {
    def classLoading = otel.mbean("java.lang:type=ClassLoading")
    otel.instrument(
        classLoading,
        "jvm.classes.loaded",
        "number of loaded classes",
        "1",
        "LoadedClassCount",
        otel.&longValueCallback
    )

    def garbageCollector = otel.mbeans("java.lang:type=GarbageCollector,*")
    otel.instrument(
        garbageCollector,
        "jvm.gc.collections.count",
        "total number of collections that have occurred",
        "1",
        ["name" : { mbean -> mbean.name().getKeyProperty("name") }],
        "CollectionCount",
        otel.&longCounterCallback
    )
    otel.instrument(
        garbageCollector,
        "jvm.gc.collections.elapsed",
        "the approximate accumulated collection elapsed time in milliseconds",
        "ms",
        ["name" : { mbean -> mbean.name().getKeyProperty("name") }],
        "CollectionTime",
        otel.&longCounterCallback
    )

    def memory = otel.mbean("java.lang:type=Memory")
    otel.instrument(
        memory,
        "jvm.memory.heap",
        "current heap usage",
        "by",
        "HeapMemoryUsage",
        otel.&longValueCallback
    )
    otel.instrument(
        memory,
        "jvm.memory.nonheap",
        "current non-heap usage",
        "by",
        "NonHeapMemoryUsage",
        otel.&longValueCallback
    )

    def memoryPool = otel.mbeans("java.lang:type=MemoryPool,*")
    otel.instrument(
        memoryPool,
        "jvm.memory.pool",
        "current memory pool usage",
        "by",
        ["name" : { mbean -> mbean.name().getKeyProperty("name") }],
        "Usage",
        otel.&longValueCallback
    )

    def threading = otel.mbean("java.lang:type=Threading")
    otel.instrument(
        threading,
        "jvm.threads.count",
        "number of threads",
        "1",
        "ThreadCount",
        otel.&longValueCallback
    )

    def operatingSystem = otel.mbeans("java.lang:type=OperatingSystem")
    otel.instrument(
        operatingSystem,
        "jvm.os.committed_virtual_memory",
        "Size of committed virtual memory",
        "1",
        "CommittedVirtualMemorySize",
        otel.&longValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.total_memory_size",
        "Total Memory Size",
        "1",
        "TotalMemorySize",
        otel.&longValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.total_physical_memory_size",
        "Total Physical Memory Size",
        "1",
        "TotalPhysicalMemorySize",
        otel.&longValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.cpu_load",
        "CPU Load",
        "1",
        "CpuLoad",
        otel.&doubleValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.process_cpu_load",
        "Process CPU Load",
        "1",
        "ProcessCpuLoad",
        otel.&doubleValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.process_cpu_time",
        "Process CPU Time",
        "1",
        "ProcessCpuTime",
        otel.&longValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.system_cpu_load",
        "System CPU Load",
        "1",
        "SystemCpuLoad",
        otel.&doubleValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.system_load_average",
        "System Load Average",
        "1",
        "SystemLoadAverage",
        otel.&doubleValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.free_memory",
        "Free Memory",
        "1",
        "FreeMemorySize",
        otel.&longValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.free_memory_physical",
        "Free Physical Memory",
        "1",
        "FreePhysicalMemorySize",
        otel.&longValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.free_swap",
        "Free Swap Space",
        "1",
        "FreeSwapSpaceSize",
        otel.&longValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.total_swap_space",
        "Total Swap Space",
        "1",
        "TotalSwapSpaceSize",
        otel.&longValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.max_file_descriptors",
        "Max File Descriptors",
        "1",
        "MaxFileDescriptorCount",
        otel.&longValueCallback
    )
    otel.instrument(
        operatingSystem,
        "jvm.os.open_file_descriptors",
        "Open File Descriptors",
        "1",
        "OpenFileDescriptorCount",
        otel.&longValueCallback
    )
}

/* =============================
 *          INVOCATION
 * =============================
 */

__instrumentCassandra()
__instrumentJVM()
