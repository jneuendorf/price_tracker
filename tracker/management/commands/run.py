from django.core.management.base import BaseCommand

from tracker.models import Page


class Command(BaseCommand):
    help = 'Runs all pages that need to according to their interval settings.'

    def handle(self, *args, **options):
        pages = Page.objects.all()
        for page in pages:
            page.run()
