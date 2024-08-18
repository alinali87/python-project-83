FROM python:3.10-slim-bookworm

COPY . /

RUN make install
RUN make start