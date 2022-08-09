FROM python:3.10-alpine
LABEL maintainer="tero.paloheimo@iki.fi"

RUN apk add --no-cache dumb-init

# Add user to run the app
ARG APPLICATION_USER=appuser
RUN adduser --no-create-home -u 1000 -D ${APPLICATION_USER}

RUN mkdir /app && chown -R ${APPLICATION_USER} /app

COPY --chown=${APPLICATION_USER}:${APPLICATION_USER} . /app
WORKDIR /app

RUN pip install --upgrade pip && \
    pip install pipenv && pipenv install --system --deploy && pip install gunicorn

EXPOSE 5000

USER ${APPLICATION_USER}
CMD ["dumb-init", "gunicorn", "--bind", "0.0.0.0:5000", "-w", "4", "menu:app"]
