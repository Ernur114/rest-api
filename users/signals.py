from django.db.models.signals import post_save
from django.dispatch import receiver

from users.models import Client
from users.tasks import ActivateAccountTask


@receiver(signal=post_save, sender=Client)
def post_registration(
    sender: Client, instance: Client, created: bool, **kwargs
):
    if created:
        ActivateAccountTask().apply_async(
            kwargs={
                "username": instance.username,
                "email": instance.email,
                "code": str(instance.activation_code),
            }
        )
