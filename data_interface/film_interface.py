
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





