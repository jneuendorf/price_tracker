from datetime import timedelta
from urllib.parse import urlparse

from django.db import models
from django.utils import timezone


class Page(models.Model):
    url = models.URLField(max_length=800, unique=True)
    html_filter_kwargs = models.TextField(blank=True)
    interval = models.PositiveSmallIntegerField()
    interval_unit = models.CharField(
        max_length=7,
        # Must be datetime.timedelta compatible
        choices=[
            ('minutes', 'minutes'),
            ('hours', 'hours'),
            ('days', 'days'),
        ],
    )
    is_active = models.BooleanField(blank=True, default=False)

    def get_last_run_result(self):
        return self.run_results.order_by('created_at').last()

    def needs_run(self):
        last_run = self.get_last_run_result()
        return (
            last_run is None
            or (
                last_run + timedelta(**{self.interval_unit: self.interval})
                <= timezone.now()
            )
        )

    # TODO: with django.db.transaction.atomic() ?
    def run(self):
        if self.is_active or not self.needs_run():
            return

        self.is_active = True
        self.save()
        print('would run...................')
        self.is_active = False
        self.save()

    def __str__(self):
        short_units = {
            'minutes': 'm',
            'hours': 'h',
            'days': 'd',
        }
        parsed_url = urlparse(self.url)
        return (
            f'{parsed_url.netloc}/…/{parsed_url.path.split("/")[-1]} @ '
            f'{self.interval}{short_units[self.interval_unit]}'
        )


class RunResult(models.Model):
    page = models.ForeignKey(
        Page,
        related_name="run_results",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)


class HtmlNode(models.Model):
    run_result = models.ForeignKey(
        RunResult,
        related_name="html_nodes",
        on_delete=models.CASCADE,
    )
    html = models.TextField()
