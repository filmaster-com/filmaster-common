"""
    Basic Data Interface classes.
"""


class BaseOutputFactoryInterface(object):

    def get_from_db(self, object_id, version):
        """
            Returns the object with the given `object_id`.
            Object should be defined by the interface.
        """
        raise NotImplementedError("interface")

    def get_dict_from_db(self, object_ids_list, version):
        """
            Returns the dictionary mapping ids in the given
            `object_ids_list` to the objects that are defined
            by the interface.
        """
        raise NotImplementedError("interface")

