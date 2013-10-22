import sorl.thumbnail
from sorl.thumbnail.images import ImageFile

from django.core.files.storage import get_storage_class
from django.conf import settings

staticfiles_storage = get_storage_class(settings.STATICFILES_STORAGE)()

def get_static_image(path):
    return ImageFile(path, staticfiles_storage)

def get_thumbnail(file, geometry, **options):
    return sorl.thumbnail.get_thumbnail(file, geometry, **options)

