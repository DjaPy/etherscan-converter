FROM python:3.10-slim

ENV FORWARDED_ALLOW_IPS=* \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/

COPY pyproject.toml /


RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev && \
    rm -rf ~/.cache/pypoetry 

COPY alembic.ini /
COPY migrations /migrations
COPY src/etherscan_converter /etherscan_converter

