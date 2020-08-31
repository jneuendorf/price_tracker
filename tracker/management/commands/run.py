from django.core.management.base import BaseCommand

from tracker.models import Page


class Command(BaseCommand):
    help = 'Runs all pages that need to according to their interval settings.'

    def handle(self, *args, **options):
        pages = Page.objects.filter(is_archived=False)
        pages_with_price_drop = []
        for page in pages:
            page.run()
            try:
                price_has_dropped, (old, new) = page.price_has_dropped()
            except ValueError:
                price_has_dropped = False

            if price_has_dropped:
                print(
                    f'Price drop detected for Page(id={page.id}) '
                    f'from {old} to {new}'
                )
                pages_with_price_drop.append(page)

        # notify about pages
        # ...
