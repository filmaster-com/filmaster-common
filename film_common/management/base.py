from django.core.management import base
from django.utils.translation import gettext
from django.utils import translation
from django.conf import settings
from optparse import make_option

from film_common.utils.log import set_verbosity_level
gettext("foo")  # circular dependency workaround

class BaseCommand(base.BaseCommand):
    def execute(self, *args, **opts):
        translation.activate(settings.LANGUAGE_CODE)

        # set console level according to verbosity
        set_verbosity_level(int(opts.get('verbosity', 0)))

        super(BaseCommand, self).execute(*args, **opts)
