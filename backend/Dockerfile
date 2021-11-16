################################################################################
#                                     Base                                     #
################################################################################
FROM python:3.10-slim as base

# Arguments & environment.
ARG gate
ARG service
ARG frontgate_version
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_SERVICE=${service}
ENV KHALEESI_FRONTGATE_VERSION=${frontgate_version}

# Metadata.
WORKDIR /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}
COPY ./requirements.txt /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./manage.py /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
RUN python -m venv .venv
RUN ./.venv/bin/pip install --upgrade pip
RUN ./.venv/bin/pip install -r requirements.txt

# Data.
COPY ./${KHALEESI_GATE}/${KHALEESI_SERVICE}/ /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./khaleesi/ /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/khaleesi/

################################################################################
#                               Development Base                               #
################################################################################
FROM base as development-base

# Arguments & environment.
ARG gate
ARG service
ARG frontgate_version
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_SERVICE=${service}
ENV KHALEESI_FRONTGATE_VERSION=${frontgate_version}

# Metadata.
WORKDIR /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}
COPY ./requirements_develop.txt /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./execute_develop.sh /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/execute.sh
RUN ./.venv/bin/pip install -r requirements_develop.txt

################################################################################
#                              Development Image                               #
################################################################################
FROM python:3.10-slim as development
LABEL environment=development

# Arguments & environment.
ARG gate
ARG service
ARG frontgate_version
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_SERVICE=${service}
ENV KHALEESI_FRONTGATE_VERSION=${frontgate_version}
ENV KHALEESI_DEBUG=true
ENV PORT=8000
ENV PYTHONPATH="/code"
ENV DJANGO_SETTINGS_MODULE="settings"

# Data.
WORKDIR /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}
COPY --from=development-base /code/ /code/
RUN chmod +x ./execute.sh

# Execute the tests.
ENTRYPOINT ["./execute.sh"]
CMD ["run"]
