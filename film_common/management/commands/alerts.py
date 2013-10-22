import requests
from film_common.management.base import BaseCommand
from film_common.utils import importlib

class Command(BaseCommand):
    def handle(self, *args, **kw):
        session = requests.session()
        for alerts_module in importlib.autodiscover('alerts'):
            for alert in alerts_module.__alerts__:
                alert.check_and_notify(requests_session=session)
