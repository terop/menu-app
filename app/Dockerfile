FROM frolvlad/alpine-python3
LABEL maintainer "Tero Paloheimo <tero.paloheimo@iki.fi>"

WORKDIR /usr/local/app
COPY . .

RUN apk update && apk add --no-cache py3-psycopg2
RUN pip install -r requirements.txt
RUN pip install gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-w", "4", "menu:app"]