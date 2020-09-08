import logging
import urllib

from django.db import models
import requests

from tracker.models import NotificationRecipient


logger = logging.getLogger(__name__)


class CallMeBotRecipient(NotificationRecipient):
    API_URL = (
        'https://api.callmebot.com/whatsapp.php'
        '?phone={phone}'
        '&apikey={api_key}'
        # '&text={message}'
    )

    phone = models.CharField(max_length=30, blank=False)
    api_key = models.CharField(max_length=7)

    def notify(self, page, previous_price, current_price):
        message = (
            f'Page \'{page.name}\' got '
            f'{str(round(previous_price - current_price, 2))} cheaper. '
            f'Check {page.url}'
        )
        # NOTE: The '+' in the phone number must not be URL encoded.
        text = urllib.parse.urlencode({'text': message})
        url = (
            f'{self.API_URL.format(phone=self.phone, api_key=self.api_key)}'
            f'&{text}'
        )
        logger.info(f'\t>> url = {url}')
        return requests.get(url)
