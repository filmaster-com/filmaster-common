from film_common.data_interface.film_interface import DisplayableFilmInterface, DisplayableFilmFactoryInterface
from film_common.utils import jsonrpc

class SimpleDisplayableFilmFactory(DisplayableFilmFactoryInterface, jsonrpc.Service):

    def __init__(self, lang='en'):
        self.lang = lang

    @classmethod
    def from_request(cls, request):
        return cls(lang=request.GET.get('lang', 'en'))

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

    def filter(self, **lookup_params):
        from film20.core.models import Film
        return [self._get_displayable_film(f) for f in Film.objects.filter(**lookup_params)]

    def get_images(self, id, type):
        from film20.core.models import Poster
        return [str(p.image) for p in Poster.objects.filter(image_type=type, object=id)]

    def get_similar_films_ids_list(self, id):
        from film20.core.models import SimilarFilm
        return list(SimilarFilm.objects.filter(film_a=id).values_list('film_b', flat=True).order_by('-number_of_votes'))

    def _get_displayable_film(self, film):
        localized_film = film.get_localized_film(self.lang)
        title = localized_film.title
        poster_path = film.poster and film.poster.name
        description = localized_film.description or localized_film.fetched_description
        production_year = str(film.release_year)
        production_countries_names_list = filter(bool, (film.production_country_list or '').split(','))
        characters_ids_list = [c.id for c in film.get_actors()]
        directors_ids_list = [d.id for d in film.get_directors()]
        return SimpleDisplayableFilm(
                    id=film.id,
                    title=title,
                    poster_path=poster_path,
                    description=description,
                    production_year=production_year,
                    production_countries_names_list=production_countries_names_list,
                    characters_ids_list=characters_ids_list,
                    directors_ids_list=directors_ids_list)

class SimpleDisplayableFilm(DisplayableFilmInterface):

    def __init__(self, **kw):
        """
            For the format of the arguments check the
            DisplayableFilmInterface get methods.
        """
        vars(self).update(kw)

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

    def __jsonhint__(self):
        return self.__class__, [], self.__dict__

