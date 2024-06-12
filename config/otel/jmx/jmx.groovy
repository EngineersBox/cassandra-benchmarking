import groovy.jmx.GroovyMBean

/* =============================
 *          CASSANDRA
 * =============================
 */

def old__instrumentCassandra() {
    def cassandraMetrics = "org.apache.cassandra.metrics"
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

    // Mapping of keyspace to table
    def scopes = [
        "*": "*"
    ]
    def serializerMetrics = [
        "Cell",
        "Cfs",
        "ClusteringKey",
        "Column",
        "AllColumns",
        "ColumnSubset",
        "IndexEntry",
        "RangeTombstoneMarker",
        "RowBody",
        "Row",
        "Partition"
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
        "FifteenMinuteRate": otel.&doubleCounterCallback,
        "FiveMinuteRate": otel.&doubleCounterCallback,
        "OneMinuteRate": otel.&doubleCounterCallback,
        "Max": otel.&doubleCounterCallback,
        "Mean": otel.&doubleCounterCallback,
        "MeanRate": otel.&doubleCounterCallback,
        "Min": otel.&doubleCounterCallback,
        // "RecentValues": otel.&longHistogram, // TODO: Check whether this works
        "StdDev": otel.&doubleCounterCallback,
    ]
    serializerTypePrefixes.each { prefix ->
        serializerMetrics.each { metric ->
            serializerMBeanAttributes.each { attribute, func ->
                scopes.each { keyspace, table ->
                    def name = "${prefix}${metric}"
                    def serializer = otel.mbeans(
                        "org.apache.cassandra.metrics:name=${name}SerializerRate,keyspace=${keyspace},scope=${table},*",
                    )
                    otel.instrument(
                        serializer,
                        "cassandra.serializer.${attribute.toLowerCase()}",
                        "Serializer ${attribute}",
                        "1",
                        [
                            "name": { mbean -> prefix },
                            "metric": { mbean -> metric },
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

    def meterAttributes = [
        "Count": otel.&longCounterCallback,
        "FifteenMinuteRate": otel.&doubleCounterCallback,
        "FiveMinuteRate": otel.&doubleCounterCallback,
        "OneMinuteRate": otel.&doubleCounterCallback,
        "MeanRate": otel.&doubleCounterCallback,
    ]
    def guageAttributes = [
      "Value": otel.&longCounterCallback
    ]
    def cacheMappings = [
      "BufferPool": [
        "scopes": [
          "chunk-cache",
          "networking"
        ],
        "metrics": [
          "Hits": meterAttributes,
          "Misses": meterAttributes,
          "Capacity": guageAttributes,
          "Size": guageAttributes,
          "UsedSize": guageAttributes
        ]
      ],
      "Cache": [
        "scopes": [
          "KeyCache",
          "RowCache",
          "CounterCache"
        ],
        "metrics": [
          "Hits": meterAttributes,
          "Misses": meterAttributes,
          "Capacity": guageAttributes,
          "Entries": guageAttributes,
          "Size": guageAttributes
        ]
      ]
    ]
    cacheMappings.each { type, mappings ->
      mappings["scopes"].each { scope ->
        mappings["metrics"].each { metric, attributes ->
          def bean = otel.mbean("org.apache.cassandra.metrics:name=${metric},scope=${scope},type=${type}")
          attributes.each { attribute, func ->
            otel.instrument(
              bean,
              "cassandra.${type.toLowerCase()}.${attribute}",
              type,
              "1",
              [
                  "metric": { mbean -> metric },
                  "scope": { mbean -> mbean.name().getKeyProperty("scope") },
              ],
              [ "${attribute}": [ "${attribute}": "${attribute}" ] ],
              func
            )
          }
        }
      }
    }
    
    def clientRequestBeans = otel.mbeans("org.apache.cassandra.metrics:type=ClientRequest,*")  
    clientRequestBeans.each { bean ->
      println("==== [MBEANS] ====\n")
      println(bean.getMBeans())
      def _mbean = bean.getMBeans()[0]
      def propertyName = _mbean.name().getKeyProperty("name")
      def propertyScope = _mbean.name().getKeyProperty("scope")
      if (propertyScope == "CASWrite" || propertyScope == "CASRead") {
        meterAttributes.each{ attribute, func ->
          otel.instrument(
            bean,
            "cassandra.client_request.${attribute}",
            "Client Request ${attribute}",
            "1",
            [
              "scope": { mbean -> propertyScope },
              "name": { mbean -> propertyName }
            ],
            [ "${attribute}": [ "${attribute}": "${attribute}" ] ],
            func
          )
        }
        return
      }
      otel.instrument(
        bean,
        "cassandra.client_request.count",
        "Client Request Count",
        "1",
        [
          "scope": { mbean -> propertyScope },
          "name": { mbean -> propertyName }
        ],
        [ "Count": [ "Count": "Count" ] ],
        otel.&longValueCallback
      )
    }

    def threadPoolBeans = otel.mbeans("org.apache.cassandra.metrics:type=ThreadPools,*")
    threadPoolBeans.each { bean ->
      otel.instrument(
        bean,
        "cassandra.thread_pool",
        "Thread Pool",
        "1",
        [
          "name": { mbean -> mbean.name().getKeyProperty("name") },
          "scope": { mbean -> mbean.name().getKeyProperty("scope") },
          "path": { mbean -> mbean.name().getKeyProperty("path") },
        ],
        "Count",
        otel.&longValueCallback
      )
    }
}

def camelToSnake(String str) {
  def regex = "([a-z])([A-Z]+)";
  def replacement = "\$1_\$2";
  return str.replaceAll(regex, replacement).toLowerCase();
}

def instrumentMBean(GroovyMBean bean) {
  def nameMappings = [
    "org.apache.cassandra.metrics": "cassandra"
  ]
  def callbackMappings = [
    "double": otel.&doubleCounterCallback,
    "long": otel.&doubleCounterCallback,
    // "[D": otel.&doubleHistogram,
    // "[J": otel.&doubleHistogram,
    "java.lang.Object": otel.&longCounterCallback
  ]
  def beanInfo = bean.info()
  def attributes = bean.listAttributeNames()
  def beanName = bean.name()
  def domain = beanName.getDomain()
  def propertyType = beanName.getKeyProperty("type")
  def propertyName = beanName.getKeyProperty("name")
  def labelMappings = beanName.getKeyPropertyList()
    .dropWhile({ k,v -> k == "type" || k == "name" })
    .collectEntries({ k,v -> [(k): { ignored -> v }] })
  beanInfo.getAttributes().each({ attribute ->
    def callback = callbackMappings[attribute.getType()]
    if (callback == null) {
      return
    }
    System.err.println("Bean name: ${beanName}")
    otel.instrument(
      otel.mbean(beanName.toString()),
      camelToSnake("${nameMappings[domain]}.${propertyType}.${propertyName}"),
      "${propertyType} ${propertyName}",
      "1",
      labelMappings,
      attribute.getName(),
      callback
    )
  })
}

def instrumentMBeans(String objectName) {
  def mbeans = otel.queryJmx(objectName)
  mbeans.each({ mbean -> 
    instrumentMBean(mbean)
  })
}

def __instrumentCassandra() {
  instrumentMBeans("org.apache.cassandra.metrics:type=Cache,*")
  instrumentMBeans("org.apache.cassandra.metrics:type=BufferPool,*")
  instrumentMBeans("org.apache.cassandra.metrics:type=ColumnFamily,*")
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

    // TODO: Rework this collection for GC since it's incorrect
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
