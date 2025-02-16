FROM --platform=$BUILDPLATFORM python:3.7-alpine AS builder

RUN apk add --no-cache postgresql-dev gcc musl-dev python3-dev

WORKDIR /app

COPY ../requirements.txt /app
RUN pip3 install -r requirements.txt --no-cache-dir
COPY .. /app

EXPOSE 8080
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "0.0.0.0:8080"]