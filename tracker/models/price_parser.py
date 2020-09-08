import inspect

from django.db import models

from tracker.util import extract_price, parse_price


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
