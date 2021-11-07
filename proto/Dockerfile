################################################################################
#                                    Python                                    #
################################################################################
FROM python:3.10-slim as python

# Arguments & environment.
ENV PYTHONUNBUFFERED=1

# Metadata.
WORKDIR /code
COPY python/ /code/python/
COPY proto /code/proto
RUN mkdir -p /data

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r python/requirements.txt

# Generate code.
CMD cp python/__init__.py /data/__init__.py && python -m grpc_tools.protoc -I proto --python_out=/data --grpc_python_out=/data --mypy_out=/data proto/*.proto
