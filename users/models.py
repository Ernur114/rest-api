import uuid
from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from dirtyfields import DirtyFieldsMixin


def save_avatar_to(instance, filename):
    return f"avatars/{instance.username}/{filename}"


class Client(DirtyFieldsMixin, AbstractUser):
    is_active = models.BooleanField(
        verbose_name="активированный аккаунт", default=False
    )
    email = models.EmailField(
        verbose_name="эл. почта", max_length=100, unique=True
    )
    activation_code = models.UUIDField(
        verbose_name="код активации", unique=True, default=uuid.uuid4
    )
    expired_code = models.DateTimeField(verbose_name="срок действия кода")
    avatar = models.ImageField(
        verbose_name="аватар пользователя",
        upload_to=save_avatar_to,
        blank=True,
        null=True,
    )
    friends = models.ManyToManyField(
        to="self", verbose_name="друзья", blank=True
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return f"{self.pk} -> {self.username} -> {self.email}"

    def save(self, *args, **kwargs):
        if self.pk:
            super().save(*args, **kwargs)
        self.expired_code = timezone.now() + timedelta(minutes=3)
        super().save(*args, **kwargs)


class FriendInvite(models.Model):
    from_client = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
        related_name="sent_friend_invites",
        verbose_name="кто",
    )
    to_client = models.ForeignKey(
        to=Client,
        on_delete=models.CASCADE,
        related_name="received_friend_invites",
        verbose_name="кого",
    )
    date_created = models.DateField(
        verbose_name="дата создания", auto_now_add=True
    )
    is_accepted = models.BooleanField(
        verbose_name="принято", null=True, default=None
    )

    class Meta:
        ordering = ("id",)
        verbose_name = "приглашение"
        verbose_name_plural = "приглашения"
        constraints = [
            models.UniqueConstraint(
                fields=["from_client", "to_client"],
                name="unique_friend_invite",
            )
        ]

    def __str__(self):
        return (f"{self.from_client} -> {self.to_client} | "
                f"{self.date_created} -> {self.is_accepted}")
