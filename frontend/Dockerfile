# syntax=docker/dockerfile:1
################################################################################
#                                     Base                                     #
################################################################################
FROM node:20.2.0-slim as base

# Arguments & environment.
ARG gate
ARG version
ENV KHALEESI_GATE=${gate}
ENV KHALEESI_VERSION=${version}

# Metadata.
WORKDIR /code
COPY ./package.json /code/
COPY ./package-lock.json /code/
COPY ./tsconfig.json /code/
COPY ./remix.config.js /code/
COPY ./remix.env.d.ts /code/
RUN sed -i "s/\${KHALEESI_GATE}/${KHALEESI_GATE}/" "/code/package.json"
RUN sed -i "s/\${KHALEESI_VERSION}/${KHALEESI_VERSION}/" "/code/package.json"
RUN sed -i "s/\${KHALEESI_GATE}/${KHALEESI_GATE}/" "/code/package-lock.json"
RUN sed -i "s/\${KHALEESI_VERSION}/${KHALEESI_VERSION}/" "/code/package-lock.json"
RUN mkdir node_modules && npm ci

# Data.
COPY ./${KHALEESI_GATE}/ /code/
RUN rm /code/app/khaleesi
COPY ./khaleesi/app/khaleesi/ /code/app/khaleesi/

################################################################################
#                               Development Base                               #
################################################################################
FROM base AS development-base

# Arguments & environment.
ARG gate
ENV KHALEESI_GATE=${gate}

# Data.
COPY ./.eslintrc.js /code/
COPY ./jest.config.js /code/
COPY execute_develop.sh /code/execute.sh

################################################################################
#                              Development Image                               #
################################################################################
FROM node:20.2.0-slim as development
LABEL environment=development

# Arguments & environment.
ARG gate
ENV PORT=8000
ENV KHALEESI_GATE=${gate}

# Data.
WORKDIR /code/frontend/${KHALEESI_GATE}/
COPY --from=development-base /code/ /code/frontend/${KHALEESI_GATE}/
RUN chmod +x ./execute.sh

# Execute the tests.
ENTRYPOINT ["./execute.sh"]
CMD ["run"]

################################################################################
#                               Production Base                                #
################################################################################
FROM base AS production-base

# Arguments & environment.
ARG gate
ENV KHALEESI_GATE=${gate}

# Data.
WORKDIR /code/
RUN npm run build
RUN ls -al

################################################################################
#                            Production Server Base                            #
################################################################################
# Data.
FROM node:20.2.0-slim as production
LABEL environment=production

# Arguments & environment.
ARG gate
ENV PORT=8000
ENV KHALEESI_GATE=${gate}

# Data.
WORKDIR /code/
COPY ./package.json /code/
COPY ./execute.sh /code/execute.sh
COPY ./remix.env.d.ts /code/
COPY --from=production-base /code/build/ /code/build/
COPY --from=production-base /code/public/build/ /code/public/build/
COPY --from=production-base /code/node_modules/@remix-run/serve/ /code/node_modules/@remix-run/serve/
COPY --from=production-base /code/node_modules/.bin/remix-serve /code/node_modules/.bin/remix-serve
RUN chmod +x ./execute.sh

# Execute the tests.
ENTRYPOINT ["./execute.sh"]
CMD ["run"]
