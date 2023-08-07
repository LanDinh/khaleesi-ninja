# syntax=docker/dockerfile:1
################################################################################
#                                     Base                                     #
################################################################################
FROM khaleesi/base/backend-construction:1.0.0 as base

# Arguments & environment.
ARG site
ARG app
ARG version
ENV SITE=${site}
ENV APP=${app}
ENV KHALEESI_VERSION=${version}

# Metadata.
WORKDIR /code/backend/${SITE}/${APP}
COPY ./manage.py /code/backend/${SITE}/${APP}/
COPY ./requirements.txt /code/backend/${SITE}/${APP}/
COPY ./${SITE}/${APP}/requirements-app.txt /code/backend/${SITE}/${APP}/
RUN --mount=type=cache,target=/root/.cache/pip,from=pip_cache ../../.venv/bin/pip install -r requirements-app.txt

################################################################################
#                               Development Base                               #
################################################################################
FROM base as development-base

# Arguments & environment.
ARG site
ARG app
ARG version
ENV SITE=${site}
ENV APP=${app}
ENV KHALEESI_VERSION=${version}

# Metadata.
WORKDIR /code/backend/${SITE}/${APP}
COPY ./requirements-develop.txt /code/backend/${SITE}/${APP}/
COPY ./mypy.ini /code/backend/${SITE}/${APP}/
COPY ./pylintrc /code/backend/${SITE}/${APP}/
COPY ./execute_develop.sh /code/backend/${SITE}/${APP}/execute.sh
RUN --mount=type=cache,target=/root/.cache/pip,from=pip_cache ../../.venv/bin/pip install -r requirements-develop.txt

# Data. Copy here instead of Base to avoid re-running pip install for dev tools.
COPY ./${SITE}/${APP}/ /code/backend/${SITE}/${APP}/
COPY ./khaleesi/ /code/backend/${SITE}/${APP}/khaleesi/

################################################################################
#                              Development Image                               #
################################################################################
FROM khaleesi/base/backend-image:1.0.0 as development

# Arguments & environment.
ARG site
ARG app
ARG version
ENV SITE=${site}
ENV APP=${app}
ENV KHALEESI_VERSION=${version}
ENV KHALEESI_DEBUG=true
ENV KHALEESI_METRICS_PORT=8020
ENV PORT=8000
ENV PYTHONPATH=/code/backend/${SITE}/${APP}:/code/backend/${SITE}/${APP}/khaleesi/proto
ENV DJANGO_SETTINGS_MODULE="settings"

# Data.
WORKDIR /code/backend/${SITE}/${APP}
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
ARG site
ARG app
ARG version
ENV SITE=${site}
ENV APP=${app}
ENV KHALEESI_VERSION=${version}

# Metadata.
WORKDIR /code/backend/${SITE}/${APP}
COPY ./execute_production.sh /code/backend/${SITE}/${APP}/execute.sh

# Data. Copy here instead of Base to avoid re-running pip install for dev tools for dev image.
COPY ./${SITE}/${APP}/ /code/backend/${SITE}/${APP}/
COPY ./khaleesi/ /code/backend/${SITE}/${APP}/khaleesi/
RUN rm -r tests

################################################################################
#                               Production Image                               #
################################################################################
FROM khaleesi/base/backend-image:1.0.0 as production

# Arguments & environment.
ARG site
ARG app
ARG version
ENV SITE=${site}
ENV APP=${app}
ENV KHALEESI_VERSION=${version}
ENV KHALEESI_METRICS_PORT=8020
ENV PORT=8000
ENV PYTHONPATH=/code/backend/${SITE}/${APP}/khaleesi/proto
ENV DJANGO_SETTINGS_MODULE="settings"

# Data.
WORKDIR /code/backend/${SITE}/${APP}
COPY --from=production-base /code/ /code/
RUN chmod +x ./execute.sh

# Execute the tests.
ENTRYPOINT ["./execute.sh"]
CMD ["run"]
