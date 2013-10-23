from data_interface.interface import BaseOutputFactoryInterface
from data_interface.film_interface import DisplayableFilmInterface


class SimpleDisplayableFilmFactory(BaseOutputFactoryInterface):

    def __init__(self, lang):
        self.lang = lang

    def get_from_db(self, object_id):
        """
            Returns the object with the given `object_id`.
            Object should be defined by the interface.
        """

        from film20.core.models import Film

        film = Film.objects.get(id=object_id)
        return self._get_displayable_film(film)

    def get_dict_from_db(self, object_ids_list):
        """
            Returns the dictionary mapping ids in the given
            `object_ids_list` to the objects that are defined
            by the interface.
        """

        from film20.core.models import Film

        displayable_film_dict = dict()
        for film in Film.objects.filter(id__in=object_ids_list):
            displayable_film_dict[film.id] = self.get_displayable_film(film)
        return displayable_film_dict

    def _get_displayable_film(self, film):
        localized_film = film.get_localized_film(self.lang)
        title = localized_film.title
        #TODO(check if this is the correct path)
        poster_path = film.get_absolute_image_url()
        description = localized_film.description or localized_film.fetched_description
        production_year = str(film.release_year)
        production_countries_names_list = film.production_country_list.split(',')
        characters_ids_list = [c.id for c in film.get_actors()]
        directors_ids_list = [d.id for d in film.get_directors()]
        return SimpleDisplayableFilm(
                    title=title,
                    poster_path=poster_path,
                    description=description,
                    production_year=production_year,
                    production_countries_names_list=production_countries_names_list,
                    characters_ids_list=characters_ids_list,
                    directors_ids_list=directors_ids_list)

class SimpleDisplayableFilm(DisplayableFilmInterface):

    def __init__(self, title, poster_path, description, production_year,
                 production_countries_names_list,
                 characters_ids_list, directors_ids_list):
        """
            For the format of the arguments check the
            DisplayableFilmInterface get methods.
        """
        self.title = title
        self.poster_path = poster_path
        self.description = description
        self.production_year = production_year
        self.production_countries_names_list = production_countries_names_list
        self.characters_ids_list = characters_ids_list
        self.directors_ids_list = directors_ids_list

    def get_title(self):
        return self.title

    def get_poster_path(self):
        return self.poster_path

    def get_description(self):
        return self.description

    def get_production_year(self):
        return self.production_year

    def get_production_countries_names_list(self):
        return self.production_countries_names_list

    def get_characters_ids_list(self):
        return self.characters_ids_list

    def get_directors_ids_list(self):
        return self.directors_ids_list
