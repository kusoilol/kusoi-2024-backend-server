FROM debian:bookworm-slim as base

RUN apt-get update -y &&  \
    apt-get install -y g++ &&  \
    apt-get install -y python3 &&  \
    apt-get install -y python-is-python3

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN chmod 700 tester.py && chmod 700 main_test.py

ARG UID_P1=10001
ARG UID_P2=10002

RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID_P1}" \
    alice
RUN echo "alice:Alkob4kVpered!" | chpasswd

RUN adduser \
    --disabled-password \
    --gecos "" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID_P2}" \
    bob
RUN echo "bob:F11TRule$" | chpasswd
