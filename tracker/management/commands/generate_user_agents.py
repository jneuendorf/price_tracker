import logging

from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from fake_useragent import UserAgent as UserAgentGenerator

from tracker.models import UserAgent


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Generates .'

    def add_arguments(self, parser):
        parser.add_argument(
            '-n',
            '--num_user_agents',
            type=int,
            default=20,
            help='Number of user agents to create',
        )
        parser.add_argument(
            '-m',
            '--mode',
            type=str,
            choices=('default', 'add', 'replace'),
            default='default',
            help=(
                'default: generate only if no user agents exist, '
                'add: add user agents to existing ones, '
                'replace: delete existing user agents before adding'
            ),
        )

    def handle(self, *args, **options):
        mode = options['mode']
        num_new_user_agents = options['num_user_agents']

        db_user_agents = UserAgent.objects.all()
        if mode == 'default':
            if db_user_agents.count() > 0:
                print(
                    'You already have user agents in the database. '
                    'Use the --mode=add or --mode=replace!'
                )
                return
        elif mode == 'replace':
            db_user_agents.delete()
        elif mode == 'add':
            pass

        user_agent_generator = UserAgentGenerator()
        num_duplicates = 0
        for i in range(num_new_user_agents):
            try:
                UserAgent.objects.create(
                    user_agent=user_agent_generator.random,
                )
            except IntegrityError:
                num_duplicates += 1

        if num_duplicates > 0:
            print(
                f'created {num_new_user_agents - num_duplicates} new user '
                f'agents ({num_duplicates} duplicates)'
            )
