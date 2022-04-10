################################################################################
#                                     Base                                     #
################################################################################
FROM python:3.10-slim as base

# Arguments & environment.
ARG gate
ARG service
ARG version
ARG frontgate_version
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_SERVICE=${service}
ENV KHALEESI_VERSION=${version}
ENV KHALEESI_FRONTGATE_VERSION=${frontgate_version}

# Prerequisites.
RUN apt-get update && apt-get install -y python3-dev libpq-dev gcc
RUN export PATH=/usr/lib/postgresql/X.Y/bin/:$PATH

# Metadata.
WORKDIR /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}
COPY ./requirements.txt /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./manage.py /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
RUN python -m venv .venv
RUN ./.venv/bin/pip install --upgrade pip
RUN ./.venv/bin/pip install -r requirements.txt

################################################################################
#                               Development Base                               #
################################################################################
FROM base as development-base

# Arguments & environment.
ARG gate
ARG service
ARG version
ARG frontgate_version
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_SERVICE=${service}
ENV KHALEESI_VERSION=${version}
ENV KHALEESI_FRONTGATE_VERSION=${frontgate_version}

# Metadata.
WORKDIR /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}
COPY ./requirements_develop.txt /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./mypy.ini /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./pylintrc /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./execute_develop.sh /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/execute.sh
RUN ./.venv/bin/pip install -r requirements_develop.txt

# Data. Copy here instead of Base to avoid re-running pip install for dev tools.
COPY ./${KHALEESI_GATE}/${KHALEESI_SERVICE}/ /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./khaleesi/ /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/khaleesi/

################################################################################
#                              Development Image                               #
################################################################################
FROM python:3.10-slim as development
LABEL environment=development

# Prerequisites.
RUN apt-get update && apt-get install -y postgresql

# Arguments & environment.
ARG gate
ARG service
ARG version
ARG frontgate_version
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_SERVICE=${service}
ENV KHALEESI_VERSION=${version}
ENV KHALEESI_FRONTGATE_VERSION=${frontgate_version}
ENV KHALEESI_DEBUG=true
ENV KHALEESI_METRICS_PORT=8020
ENV PORT=8000
ENV PYTHONPATH=/code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}:/code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/khaleesi/proto
ENV DJANGO_SETTINGS_MODULE="settings"

# Data.
WORKDIR /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}
COPY --from=development-base /code/ /code/
RUN chmod +x ./execute.sh

# Execute the tests.
ENTRYPOINT ["./execute.sh"]
CMD ["run"]

################################################################################
#                               Production Base                                #
################################################################################
FROM base as production-base

# Arguments & environment.
ARG gate
ARG service
ARG version
ARG frontgate_version
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_SERVICE=${service}
ENV KHALEESI_VERSION=${version}
ENV KHALEESI_FRONTGATE_VERSION=${frontgate_version}

# Metadata.
WORKDIR /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}
COPY ./execute_production.sh /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/execute.sh

# Data. Copy here instead of Base to avoid re-running pip install for dev tools for dev image.
COPY ./${KHALEESI_GATE}/${KHALEESI_SERVICE}/ /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./khaleesi/ /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/khaleesi/
RUN rm -r tests

################################################################################
#                               Production Image                               #
################################################################################
FROM python:3.10-slim as production
LABEL environment=production

# Prerequisites.
RUN apt-get update && apt-get install -y postgresql

# Arguments & environment.
ARG gate
ARG service
ARG version
ARG frontgate_version
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_SERVICE=${service}
ENV KHALEESI_VERSION=${version}
ENV KHALEESI_FRONTGATE_VERSION=${frontgate_version}
ENV KHALEESI_METRICS_PORT=8020
ENV PORT=8000
ENV PYTHONPATH=/code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/khaleesi/proto
ENV DJANGO_SETTINGS_MODULE="settings"

# Data.
WORKDIR /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}
COPY --from=production-base /code/ /code/
RUN chmod +x ./execute.sh

# Execute the tests.
ENTRYPOINT ["./execute.sh"]
CMD ["run"]
