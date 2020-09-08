from django.db import models

from .page import Page


class RunResult(models.Model):
    page = models.ForeignKey(
        Page,
        related_name="run_results",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_prices(self):
        return [node.price for node in self.html_nodes.all()]

    def __str__(self):
        return (
            f'<RunResult '
            f'page="{self.page.get_readable_url()}" '
            f'prices={str(self.get_prices())}>'
        )
