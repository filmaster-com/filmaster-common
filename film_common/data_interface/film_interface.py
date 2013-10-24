from .interface import BaseOutputFactoryInterface

class DisplayableFilmFactoryInterface(BaseOutputFactoryInterface):

    IMAGE_TYPE_POSTER = 1
    IMAGE_TYPE_BACKDROP = 2

    def get_images(self, id, type):
        raise NotImplementedError

    def get_similar_films_ids_list(self, id):
        raise NotImplementedError

class DisplayableFilmInterface(object):

    def get_title(self):
        """
            Returns the title of the film.
        """
        raise NotImplementedError("interface")

    def get_poster_path(self):
        """
            Returns the absolute path to the film's poster.
        """
        raise NotImplementedError("interface")

    def get_description(self):
        """
            Returns the description of the film.
        """
        raise NotImplementedError("interface")

    def get_production_year(self):
        """
            Returns the production year of the film (string).
        """
        raise NotImplementedError("interface")

    def get_production_countries_names_list(self):
        """
            Returns the list of production countries
            of the film (list of strings).
        """
        raise NotImplementedError("interface")

    def get_characters_ids_list(self):
        """
            Returns the ids of characters staring
            in the film (list of strings).
        """
        raise NotImplementedError("interface")

    def get_directors_ids_list(self):
        """
            Returns the ids of film directors (list of strings).
        """
        raise NotImplementedError("interface")

    IMAGE_TYPE_POSTER = 1
    IMAGE_TYPE_BACKDROP = 2

    def get_images(self, type):
        """
            Returns film images of provided type
        """
        raise NotImplementedError("interface")

def get_default_displayable_film_factory():
    from film_common.utils import jsonrpc
    from django.conf import settings
    return jsonrpc.Server(settings.DISPLAYABLE_FILM_FACTORY)

