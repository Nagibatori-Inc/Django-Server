FROM python:3.9.15-slim-buster AS builder

RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    bash \
    curl \
    build-essential \
    libpq-dev

WORKDIR /app

COPY ./requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /app

EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0.0.0.0:8080"]