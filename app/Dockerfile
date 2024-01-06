LABEL maintainer="tero.paloheimo@iki.fi"

FROM python:3.11-alpine as python
ENV PYTHONUNBUFFERED=true
RUN apk update && apk upgrade && python3 -m pip install --upgrade pip

RUN apk add --no-cache dumb-init

# Add user to run the app
ARG APPLICATION_USER=appuser
RUN adduser --no-create-home -u 1000 -D ${APPLICATION_USER}

RUN mkdir /usr/src/app && chown -R ${APPLICATION_USER} /usr/src/app

COPY --chown=${APPLICATION_USER}:${APPLICATION_USER} \
    db.py menu.py templates/ menu.cfg poetry.lock /usr/src/app
WORKDIR /usr/src/app

FROM python as poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
ENV PATH="${POETRY_HOME}/bin:${PATH}"
RUN python -c 'from urllib.request import urlopen; print(urlopen("https://install.python-poetry.org").read().decode())' | python -
COPY . ./
RUN poetry install --no-interaction --no-ansi -vv

FROM python as runtime
ENV PATH="/usr/src/app/.venv/bin:${PATH}"
COPY --from=poetry /usr/src/app /usr/src/app

RUN pip install gunicorn

EXPOSE 5000

USER ${APPLICATION_USER}
CMD ["dumb-init", "gunicorn", "--bind", "0.0.0.0:5000", "-w", "4", "menu:app"]
