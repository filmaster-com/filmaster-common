#from film_common.utils.jsonrpc import Server

PAGE_LIMIT=300

class ProxyAPI(object):

    #def __init__(self, app_id):
    #    from django.conf import settings
    #    self.server = Server(settings.PROXY_URI)
    #    self.server.connect(app_id)
    #    return super(ProxyAPI, self).__init__()

    #def get_friend_id_list(self, hash_id):
    #    return self.server.get_friend_id_list(hash_id)

    #def get_close_friends_list(self, hash_id):
    #    return self.server.get_close_friends_list(hash_id)

    #def get_family_list(self, hash_id):
    #    return self.server.get_family_list(hash_id)

    #def get_like_ids(self, hash_id):
    #    return self.server.get_like_ids(hash_id)

    #def get_recent_likes(self, hash_id):
    #    return self.server.get_recent_likes(hash_id)

    #def get_object_by_id(self, hash_id, fields=None):
    #    return self.server.get_object_by_id(hash_id)

    RECENT_LIKES_PAGES = 1

    def __init__(self, access_token):
        self.access_token = access_token
        from film_common.utils.fb.graph import API
        self.api = API(access_token)

    def get_friend_id_list(self, hash_id):
        return self.fetch_with_pagination('/' + hash_id + '/friends', fields='id')

    def get_close_friends_list(self, hash_id):
        return set(self.fetch_with_pagination('/' + hash_id + '/friendlists/close_friends', fields='members'))

    def get_family_list(self, hash_id):
        return self.fetch_with_pagination('/' + hash_id + '/friendlists/family', fields='members')

    def get_like_ids(self, hash_id):
        return self.fetch_with_pagination('/' + hash_id + '/likes', fields='id')

    def get_recent_likes(self, hash_id):
        return self.fetch_with_pagination('/' + hash_id + '/likes', fields='id,name,category,created_time', limit=ProxyAPI.RECENT_LIKES_PAGES)

    def get_watched_movies(self, hash_id):
        fb_obj = self.fetch_with_pagination('/' + hash_id + '/video.watches', handler=lambda x: x)
        return self.flatten_movie_data(fb_obj)

    def get_wants_to_watch(self, hash_id):
        fb_obj = self.fetch_with_pagination('/' + hash_id + '/video.wants_to_watch', handler=lambda x: x)
        return self.flatten_movie_data(fb_obj)


    def get_movies(self, hash_id):
        return self.fetch_with_pagination('/' + hash_id + '/movies', fields='id')

    def get_object_by_id(self, hash_id, fields=None):
        return self.api.get('/' + hash_id)

    def fetch_with_pagination(self, initial_path, fields=None, handler=lambda data: (x['id'] for x in data), limit=None):
        path = initial_path
        handler_results = []
        while True and (limit is None or limit > 0):
            if fields:
                objs = self.api.get(path, fields=fields, limit=PAGE_LIMIT)
            else:
                objs = self.api.get(path)
            data = objs.get('data', ())
            handler_results += handler(data)
            paging = objs.get('paging')
            path = paging and paging.get('next')
            if limit:
                limit -= 1
            if not path:
                break
        return handler_results

    def flatten_movie_data(self, fb_obj):
        result = []
        for item in fb_obj:
            data_obj = item.get('data', None)
            if data_obj:
                movie_obj = data_obj.get('movie', None)
                if movie_obj:
                    id_ = movie_obj.get('id', None)
                    if id_:
                        result.append(id_)
        return result
