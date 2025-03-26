from celery import Celery

app = Celery("DjangoServer")
app.config_from_object("django_conf:settings", namespace="CELERY")
app.autodiscover_tasks()
