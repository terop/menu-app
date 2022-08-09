FROM python:3.10-alpine
LABEL maintainer="tero.paloheimo@iki.fi"

RUN apk add --no-cache dumb-init

WORKDIR /usr/src/app
COPY . .

RUN pip install --upgrade pip && \
    pip install pipenv && pipenv install --system --deploy && pip install gunicorn
EXPOSE 5000
CMD ["dumb-init", "gunicorn", "--bind", "0.0.0.0:5000", "-w", "4", "menu:app"]
