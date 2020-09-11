import logging

from django.core.management.base import BaseCommand

from tracker.models import Page, UserAgent


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Runs all pages that need to according to their interval settings.'

    def handle(self, *args, **options):
        pages = Page.objects.filter(is_archived=False)
        pages_with_price_drop = []
        user_agents = UserAgent.objects.all()

        for page in pages:
            page.run(user_agents=user_agents)

            try:
                previous, current = page.get_price_drop()
            except ValueError:
                previous, current = -1, -1

            price_has_dropped = current < previous
            if price_has_dropped:
                pages_with_price_drop.append((page, previous, current))

        for page, previous_price, current_price in pages_with_price_drop:
            logger.info(
                f'Price drop detected for \'{page.name}\' '
                f'from {previous_price} to {current_price}'
            )
            for recipient in page.notification_recipients.all():
                response = recipient.notify(
                    page,
                    previous_price,
                    current_price,
                )
                logger.info(
                    f'notified {recipient.first_name} {recipient.last_name} '
                    f'({response.status_code})'
                )
            logger.info('\n')
