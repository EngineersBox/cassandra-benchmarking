import groovy.jmx.GroovyMBean
import groovy.transform.EqualsAndHashCode
import javax.management.ObjectName
import java.util.ArrayList

/* =============================
 *     AUTO-INSTRUMENTATION
 * =============================
 */

class Cache {

  @EqualsAndHashCode
  static class Key {
      def domain;
      def name;
      def type;
      def labels // List of string names
      def metricClass; // JmxGauge, JmxTimer, etc

      String toIndentedString(final String indent) {
        String labelNames = this.labels.collect({
            label -> "${indent}    ${label}"
        }).join(",\n")
        return """${indent}Key: {
${indent}  Domain: ${this.domain},
${indent}  Name: ${this.name},
${indent}  Type: ${this.type},
${indent}  Labels: [
${labelNames}
${indent}  ],
${indent}  Metric Class: ${this.metricClass}
${indent}}""";
      }
  }

  @EqualsAndHashCode
  static class Attribute {
      def name;
      def desc;
      def unit;
      def labelMappings; // Map of String to Closure
      def callbackType;
      def callback;

      String toIndentedString(final String indent) {
        String lindent = "${indent}    ";
        String labels = this.labelMappings.collect({
            label, closure -> "${lindent}${label}"
        }).join(",\n");
        return """${indent}Attribute: {
${indent}  Name: ${this.name},
${indent}  Desc: ${this.desc},
${indent}  Unit: ${this.unit},
${indent}  Labels: [
${labels}
${indent}  ],
${indent}  Callback Type: ${this.callbackType}
${indent}}""";
      }

  }

  @EqualsAndHashCode
  static class Entry {
      Set<String> objectNames;
      Map<String, Cache.Attribute> attributes
    
      String toIndentedString(final String indent) {
          String objectNamesString = this.objectNames.collect({
              on -> "${indent}    ${on}"
          }).join(",\n");
          String aindent = "${indent}    ";
          String attributesString = this.attributes.collect({
              name, attribute -> "${aindent}Name: ${name},\n${attribute.toIndentedString(aindent)}"
          }).join(",\n");
          return """${indent}Entry: {
${indent}  Object Names: [
${objectNamesString}
${indent}  ],
${indent}  Attributes: {
${attributesString}
${indent}  }
${indent}}""";
      }
  }

  static boolean initialised = false
  static Map<Cache.Key, Cache.Entry> mbeanMappings = [:]

  static def printCache() {
      Cache.mbeanMappings.each({ key, entry ->
          System.err.println("""{
${key.toIndentedString("  ")}
${entry.toIndentedString("  ")}
}""");
      })
  }
}

@EqualsAndHashCode
class ConditionalAttributes {
    Set<String> trueExclusionAttributes;
    Set<String> falseExclusionAttributes;
}

def camelToSnake(String str) {
  def regex = "([a-z])([A-Z]+)";
  def replacement = "\$1_\$2";
  return str.replaceAll(regex, replacement).toLowerCase();
}

def resolveGaugeValueType(GroovyMBean bean) {
  def value = bean.getProperty("Value")
  def clazz = value.getClass()
  def typeName = clazz.getName().replace(
    "${clazz.getPackageName()}.",
    ""
  )
  return "${Character.toLowerCase(typeName.charAt(0))}${typeName.substring(1)}"
}

def enforceNaming(def str) {
    return str == null ? "" : "." + str.replaceAll("\s", "_")
        .replaceAll("[^a-zA-Z0-9_]+", "_")
}

def constructName(def domain, def propertyType, def propertyName, def attributeName) {
  def formattedPropertyType = enforceNaming(propertyType)
  def formattedPropertyName = enforceNaming(propertyName)
  return "${domain}${formattedPropertyType}${formattedPropertyName}.${attributeName}"
}

def formatDescSection(def section) {
  return section == null ? "" : "${section} "
}

def cacheMBean(GroovyMBean bean, def nameMappings, final Map<String, ConditionalAttributes> conditionalAttributes) {
  def callbackMappings = [
    "double": otel.&doubleValueCallback,
    "long": otel.&doubleValueCallback,
    "integer": otel.&doubleValueCallback,
    // "[D": otel.&doubleHistogram,
    // "[J": otel.&longHistogram,
    // "java.lang.Object": otel.&longCounterCallback
  ]
  def beanInfo = bean.info()
  def attributes = bean.listAttributeNames()
  def beanName = bean.name()
  def metricClassSplit = beanInfo.getClassName().tokenize('$')
  def metricClass = metricClassSplit.last()
  def isGauge = metricClass == "JmxGauge"
  def domain = beanName.getDomain()
  def propertyType = beanName.getKeyProperty("type")
  def propertyName = beanName.getKeyProperty("name")
  def labelMappings = beanName.getKeyPropertyList()
    .findAll({ k,v -> k != "type" && k != "name" })
    .collectEntries({ k,v -> [(k): { mbean -> mbean.name().getKeyProperty(k) }] })
  final Cache.Key key = new Cache.Key(
      domain: domain,
      name: propertyName,
      type: propertyType,
      labels: labelMappings.collect({ k,v -> k}),
      metricClass: metricClass
  );
  Cache.Entry entry = Cache.mbeanMappings.computeIfAbsent(key, { k -> new Cache.Entry(
      objectNames: [],
      attributes: [:]
  )});
  entry.objectNames.add(beanName.toString());
  def beanAttributes = conditionalAttributes == null
      ? beanInfo.getAttributes()
      : beanInfo.getAttributes()
          .findAll({ attribute -> !conditionalAttributes.containsKey(attribute.getName()) })
  conditionalAttributes?.each({
      cond, attrs ->
      System.err.println("Condition attribute: ${cond} => ${bean.getProperty(cond).getClass()}: ${bean.getProperty(cond)}");
      final boolean enabled = bean.getProperty(cond)
      if (enabled) {
          System.err.println("Running true exclusions: ${attrs.trueExclusionAttributes}");
          beanAttributes = beanAttributes.findAll({ beanAttribute ->
              String attrName = beanAttribute.getName()
              boolean state = !attrs.trueExclusionAttributes.contains(attrName)
              System.err.println("Attribute: ${attrName} => ${state}");
              return state;
          })
      } else {
          System.err.println("Running false exclusions: ${attrs.falseExclusionAttributes}");
          beanAttributes = beanAttributes.findAll({ beanAttribute ->
              String attrName = beanAttribute.getName()
              boolean state = !attrs.falseExclusionAttributes.contains(attrName)
              System.err.println("Attribute: ${attrName} -> ${state}")
              return state
          })
      }
  })
  if (conditionalAttributes != null) {
      System.err.println(beanAttributes.collect({ attr -> attr.getName() }))
  }
  beanAttributes.each({ attribute ->
    def mappingLookupKey = isGauge || attribute?.getType() == "java.lang.Object"
        ? resolveGaugeValueType(bean)
        : attribute.getType()
    def callback = callbackMappings[mappingLookupKey]
    if (callback == null) {
      return
    }
    def attributeName = attribute.getName()
    entry.attributes.putIfAbsent(attributeName, new Cache.Attribute(
        name: camelToSnake(constructName(
            nameMappings[domain],
            propertyType,
            propertyName,
            attributeName
        )),
        desc: "${formatDescSection(propertyType)}${formatDescSection(propertyName)}${attributeName}",
        unit: "1",
        labelMappings: labelMappings,
        callbackType: mappingLookupKey,
        callback: callback
    ));
  })
}

def cacheMBeans(final String objectName,
                final Map<String, String> nameMappings,
                final List<ObjectName> excludeObjectNames = [],
                final Map<ObjectName, Map<String, ConditionalAttributes>> includeAttributesCond = [:]) {
  if (Cache.initialised) {
    return
  }
  def mbeans = otel.queryJmx(objectName)
  mbeans.findAll({
    mbean -> 
        def name = mbean.name()
        return !excludeObjectNames.any({ exclude -> exclude.apply(name) })
  }).each({
    mbean -> cacheMBean(
        mbean,
        nameMappings,
        includeAttributesCond.find({
            name, _cond -> name.apply(mbean.name())
        })?.getValue()
    )
  })
}

def instrumentMBeans() {
  Cache.mbeanMappings.each({ key, entry ->
      def mbeans = otel.mbeans((entry.objectNames) as ArrayList);
      entry.attributes.each({ name, attribute ->
          otel.instrument(
              mbeans,
              attribute.name,
              attribute.desc,
              attribute.unit,
              attribute.labelMappings,
              name,
              attribute.callback
          );
      })
  })
}

/* =============================
 *          CASSANDRA
 * =============================
 */

def cacheCassandraMBeans() {
  if (!Cache.initialised) {
      def nameMappings = [
          "org.apache.cassandra.metrics": "cassandra"
      ]
      cacheMBeans("org.apache.cassandra.metrics:type=Cache,*", nameMappings)
      cacheMBeans("org.apache.cassandra.metrics:type=BufferPool,*", nameMappings)
      cacheMBeans("org.apache.cassandra.metrics:type=ThreadPools,*", nameMappings)
      cacheMBeans("org.apache.cassandra.metrics:type=StorageProxy,*", nameMappings)
      cacheMBeans("org.apache.cassandra.metrics:type=ColumnFamily,*", nameMappings)
  }
}

/* =============================
 *             JVM
 * =============================
 */

def cacheJVMMBeans() {
    if (!Cache.initialised) {
        def nameMappings = [
            "java.lang": "jvm"
        ]
        def conditions = [
            (new ObjectName("java.lang:type=MemoryPool,*")): [
                "CollectionUsageThresholdSupported": new ConditionalAttributes(
                    trueExclusionAttributes: [],
                    falseExclusionAttributes: [
                        "CollectionUsage",
                        "CollectionUsageThreshold",
                        "CollectionUsageThresholdCount",
                        "CollectionUsageThresholdExceeded"
                    ]
                ),
                "UsageThresholdSupported": new ConditionalAttributes(
                    trueExclusionAttributes: [],
                    falseExclusionAttributes: [
                        "Usage",
                        "UsageThreshold",
                        "UsageThresholdCount",
                        "UsageThresholdExceeded"
                    ]
                )
            ]
        ]
        cacheMBeans("java.lang:*", nameMappings, [], conditions)
    }
}

/* =============================
 *          INVOCATION
 * =============================
 */

def instrument() {
    if (!Cache.initialised) {
        cacheCassandraMBeans()
        cacheJVMMBeans()
        Cache.initialised = true
        Cache.printCache();
    }
    instrumentMBeans()
}

instrument()
