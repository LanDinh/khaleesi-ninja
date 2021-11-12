################################################################################
#                                     Base                                     #
################################################################################
FROM ubuntu:latest as base

# Data.
WORKDIR /code
RUN apt-get update && apt-get install -y letsencrypt sudo
RUN mkdir -p /data/
COPY refresh_tls_certificate.sh /code/
RUN chmod +x ./refresh_tls_certificate.sh

# Execute the tests.
ENTRYPOINT ["./refresh_tls_certificate.sh"]
