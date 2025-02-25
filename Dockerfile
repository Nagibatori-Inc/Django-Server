FROM python:3.9.15-slim-buster AS builder

RUN apt-get update && apt-get upgrade -y \
  && apt-get install --no-install-recommends -y \
    git \
    bash \
    curl \
    build-essential \
    libpq-dev

WORKDIR /app

COPY ./requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . /app

RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 8080
CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]