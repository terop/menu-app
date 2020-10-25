FROM python:3.8.6-slim-buster
LABEL maintainer="tero.paloheimo@iki.fi"

WORKDIR /usr/local/app
COPY . .

# Install dependencies for psycogpg2
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev libpq-dev && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt
RUN pip install gunicorn
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-w", "4", "menu:app"]
