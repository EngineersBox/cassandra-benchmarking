FROM grafana/otel-lgtm

RUN yum install -y java-17-openjdk
RUN echo 'export JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")' >> ~/.bashrc
