from datetime import timedelta
import logging
import traceback
from urllib.parse import urlparse

from django.db import models
from django.utils import timezone
import requests

from tracker.util import find_html_nodes
from .price_parser import PriceParser


logger = logging.getLogger(__name__)


class Page(models.Model):
    name = models.CharField(max_length=80)
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
    is_archived = models.BooleanField(blank=True, default=False)

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
        # TODO: Declutter cyclic dependency
        from .run_result import RunResult

        if not force and (self.is_active or not self.needs_run()):
            logger.info(f'skipping {self.name}')
            return

        self.is_active = True
        self.save()
        try:
            response = requests.get(self.url)
            html = response.text
            html_nodes = find_html_nodes(html, self.css_selector)

            if test:
                logger.info(
                    f'found nodes {"".join(str(node) for node in html_nodes)}'
                )
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

        self.is_active = False
        self.save()
        logger.info(f'successfully ran {self.name}')

    def get_price_drop(self):
        run_results = self.run_results.order_by('-created_at')
        if len(run_results) == 0:
            return (-1, -1)

        if len(run_results) >= 2:
            last, next_to_last = run_results[0:2]
        else:
            last = next_to_last = run_results[0]

        prices_last = last.get_prices()
        prices_next_to_last = next_to_last.get_prices()

        if len(prices_last) == 1 and len(prices_next_to_last) == 1:
            return (prices_next_to_last[0], prices_last[0])

        raise ValueError(
            'Could not determine if the price has dropped because price is '
            f'not definite for either Page(id={last.id}) -> {prices_last} or '
            f'Page(id={next_to_last.id}) -> {prices_next_to_last}'
        )

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
