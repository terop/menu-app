FROM python:3.5-alpine
MAINTAINER "Tero Paloheimo <tero.paloheimo@iki.fi>"

RUN echo "@edge http://nl.alpinelinux.org/alpine/edge/main" >> /etc/apk/repositories && \
apk update && apk add curl "postgresql-dev" "gcc" "python3-dev" "musl-dev"
COPY app /usr/local/app/
# WORKDIR /usr/local/app/app
COPY tests /usr/local/tests/
# WORKDIR /usr/local/app/tests
WORKDIR /usr/local
RUN pip install -r app/requirements.txt
RUN pip install -r tests/requirements.txt
EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["app/menu.py"]
