################################################################################
#                                     Base                                     #
################################################################################
FROM node:16.13-slim as base

# Arguments & environment.
ARG gate
ENV KHALEESI_GATE=${gate}

# Data.
WORKDIR /code
COPY ./package.json /code/frontgate/${KHALEESI_GATE}/
COPY ./package-lock.json /code/frontgate/${KHALEESI_GATE}/
COPY ./tsconfig.json /code/frontgate/${KHALEESI_GATE}/
COPY ./core/src/core /code/frontgate/${KHALEESI_GATE}/src/core/
COPY ./${KHALEESI_GATE} /code/frontgate/${KHALEESI_GATE}/

# Install dependencies.
RUN npm ci --prefix /code/frontgate/${KHALEESI_GATE}/

################################################################################
#                               Development Base                               #
################################################################################
FROM base AS development-base

# Arguments & environment.
ARG gate
ENV KHALEESI_GATE=${gate}

# Data.
COPY ./.eslintrc.json /code/frontgate/${KHALEESI_GATE}/
COPY ./execute_tests.sh /code/frontgate/${KHALEESI_GATE}/
RUN chmod +x frontgate/${KHALEESI_GATE}/execute_tests.sh

################################################################################
#                              Development Image                               #
################################################################################
FROM node:16.13-slim as development

# Arguments & environment.
ARG gate
ENV KHALEESI_GATE=${gate}

# Data.
COPY --from=development-base /code/ /code/

# Execute the tests.
CMD ./execute_tests.sh
