from locust import HttpUser, task, between
from random import randint


class LoadTestAuth(HttpUser):
    wait_time = between(1, 5)

    @task
    def login(self):
        pass

    @task
    def verify(self):
        pass

    @task
    def send_code(self):
        pass

    @task
    def sign_up(self):
        pass

    @task
    def retrieve_profile(self):
        profile_id = randint(1, 10)
        self.client.get(f"/profiles/{profile_id}")

    @task
    def update_profile(self):
        pass

    @task
    def delete_profile(self):
        pass
