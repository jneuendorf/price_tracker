from django.db import models

from tracker.util import soup
from .run_result import RunResult


class HtmlNode(models.Model):
    run_result = models.ForeignKey(
        RunResult,
        related_name="html_nodes",
        on_delete=models.CASCADE,
    )
    html = models.TextField()
    price = models.FloatField(blank=True, null=True)

    def __str__(self):
        first_child = list(soup(self.html).select('body')[0].children)[0]
        return f'<HtmlNode tag="{first_child.name}" price={self.price}>'
