################################################################################
#                                     Base                                     #
################################################################################

FROM envoyproxy/envoy-alpine:v1.20.0
COPY ./envoy.yml /etc/envoy/envoy.yaml
CMD /usr/local/bin/envoy -c /etc/envoy/envoy.yaml
