import abc

from django.db import models
import requests


class NotificationRecipient(models.Model):
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    pages = models.ManyToManyField(
        'Page',
        related_name='notification_recipients',
        blank=True,
    )

    class Meta:
        abstract = True

    @abc.abstractmethod
    def notify(
        self,
        page,
        previous_price: float,
        current_price: float,
    ) -> requests.Response:
        pass

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
