from datetime import timedelta
import inspect
import logging
import traceback
from urllib.parse import urlparse

from django.db import models
from django.utils import timezone
import requests

from .util import soup, find_html_nodes, parse_price, extract_price


logger = logging.getLogger(__name__)


class PriceParser(models.Model):
    name = models.CharField(max_length=20)
    decimal_separator = models.CharField(max_length=1)
    parse_func = models.TextField(default=inspect.getsource(parse_price))

    def parse_price(self, x: str) -> float:
        exec_locals = {}
        exec(self.parse_func, globals(), exec_locals)
        name, func = exec_locals.popitem()
        return func(x, self.decimal_separator)

    def get_price(self, node) -> float:
        return self.parse_price(extract_price(node))

    def __str__(self):
        return self.name


class Page(models.Model):
    url = models.URLField(max_length=800, unique=True)
    css_selector = models.CharField(max_length=200)
    price_parser = models.ForeignKey(
        PriceParser,
        on_delete=models.PROTECT,
    )
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
                (
                    last_run.created_at
                    + timedelta(**{self.interval_unit: self.interval})
                )
                <= timezone.now()
            )
        )

    # TODO: with django.db.transaction.atomic() ?
    def run(self, force=False, test=False):
        if not force and (self.is_active or not self.needs_run()):
            return

        self.is_active = True
        self.save()
        try:
            response = requests.get(self.url)
            html = response.text
            html_nodes = find_html_nodes(html, self.css_selector)

            if test:
                print('found nodes', [str(node) for node in html_nodes])
            else:
                run_result = RunResult.objects.create(page=self)
                for node in html_nodes:
                    run_result.html_nodes.create(
                        html=node.prettify(),
                        price=self.price_parser.get_price(node),
                    )
        except Exception as e:
            logger.error(str(e))
            logger.error(traceback.print_exc())
            print(e, traceback.print_exc())

        # TODO: log success
        self.is_active = False
        self.save()

    def get_readable_url(self):
        parsed_url = urlparse(self.url)
        return f'{parsed_url.netloc}/…/{parsed_url.path.split("/")[-1]}'

    def __str__(self):
        short_units = {
            'minutes': 'm',
            'hours': 'h',
            'days': 'd',
        }
        return (
            f'<Page url="{self.get_readable_url()}" '
            f'css_selector="{self.css_selector}" '
            f'interval="{self.interval}{short_units[self.interval_unit]}">'
        )


class RunResult(models.Model):
    page = models.ForeignKey(
        Page,
        related_name="run_results",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        prices = [node.price for node in self.html_nodes.all()]
        return (
            f'<RunResult '
            f'page="{self.page.get_readable_url()}" '
            f'prices={str(prices)}>'
        )


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
        # print(soup(self.html).select('body').prettify())
        return f'<HtmlNode tag="{first_child.name}" price={self.price}>'
