""""
Django command to wait for Database connection
"""

from django.core.management import BaseCommand

import time
from psycopg2 import OperationalError as Psycopg2Error
from django.db.utils import OperationalError


class Command(BaseCommand):

    """Django command to wait for Database connection"""
    def handle(self, *args, **options):
        self.stdout.write("Waiting for Database connection ....")
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write("Database is not available waiting 1 sec")
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("Database is available"))
