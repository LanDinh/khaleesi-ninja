################################################################################
#                                     Base                                     #
################################################################################
FROM python:3.10-slim as base

# Arguments & environment.
ARG gate
ARG service
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_SERVICE=${service}

# Metadata.
WORKDIR /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}
COPY ./requirements.txt /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./manage.py /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./execute_develop.sh /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/execute.sh
RUN python -m venv .venv
RUN ./.venv/bin/pip install --upgrade pip
RUN ./.venv/bin/pip install -r requirements.txt

# Data.
COPY ./${KHALEESI_GATE}/${KHALEESI_SERVICE}/ /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/
COPY ./khaleesi/ /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}/khaleesi/

################################################################################
#                              Development Image                               #
################################################################################
FROM python:3.10-slim as development
LABEL environment=development

# Arguments & environment.
ARG gate
ARG service
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_SERVICE=${service}
ENV PYTHONPATH="/code"
ENV DJANGO_SETTINGS_MODULE="settings"

# Data.
WORKDIR /code/backend/${KHALEESI_GATE}/${KHALEESI_SERVICE}
COPY --from=base /code/ /code/
RUN chmod +x ./execute.sh

# Execute the tests.
ENTRYPOINT ["./execute.sh"]
CMD ["run"]