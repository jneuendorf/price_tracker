from random import randint

from django.db import models


class UserAgent(models.Model):
    user_agent = models.TextField(unique=True)

    @classmethod
    def random(cls, queryset=None):
        if queryset is None:
            queryset = cls.objects.all()

        count = len(queryset)
        random_index = randint(0, count - 1)
        return queryset[random_index].user_agent

    def __str__(self):
        return self.user_agent
