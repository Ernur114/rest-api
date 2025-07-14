from celery import Task

from common.mail import send_email
from settings import celery_app


class ActivateAccountTask(Task):
    name = "activate-account"
    default_retry_delay = 60

    def run(self, username: str, email: str, code: str):
        try:
            send_email(
                template="activation.html",
                context={
                    "username": username,
                    "code": f"http://127.0.0.1:8000/api/v1/users/activate/{code}",
                },
                to=email,
                title="Confirm your account",
            )
        except Exception as e:
            self.retry(exc=e, countdown=60 * (self.request.retries + 1))


celery_app.register_task(task=ActivateAccountTask())
