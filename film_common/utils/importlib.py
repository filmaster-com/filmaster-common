#-------------------------------------------------------------------------------
# Filmaster - a social web network and recommendation engine
# Copyright (c) 2012 Filmaster
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#-------------------------------------------------------------------------------
from django.utils.importlib import import_module
import logging
logger = logging.getLogger(__name__)

def autodiscover(module, installed_apps=None):
    import sys
    if not installed_apps:
        from django.conf import settings
        installed_apps = settings.INSTALLED_APPS
    for app in installed_apps:
        try:
            yield import_module("%s.%s" % (app, module))
        except ImportError, e:
            pass
        except:
            logger.exception('autodiscover')

def _import_object(path):
    try:
        module, name = path.rsplit('.', 1)
        return getattr(import_module(module), name)
    except (ValueError, ImportError, AttributeError), e:
        logger.warning(e)

def import_object(path):
    names = []

    while '.' in path:
        try:
            path, name = path.rsplit('.', 1)
            names.insert(0, name)
            obj = import_module(path)
            for n in names:
                obj = getattr(obj, n)
            return obj
        except ImportError, e:
            pass
        except AttributeError, e:
            logger.warning(e)
            return

