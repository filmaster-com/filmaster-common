import urllib, urllib2
import json
import logging
logger = logging.getLogger(__name__)

class API(object):
    def __init__(self, access_token=None):
        self.access_token = access_token

    BASE_URL = 'https://graph.facebook.com'

    json_response = True

    def get_access_token( self, APP_ID, APP_SECRET ):
        params = {
            'client_id'    : APP_ID,
            'client_secret': APP_SECRET,
            'grant_type'   : 'client_credentials'
        }
        response = urllib2.urlopen( 'https://graph.facebook.com/oauth/access_token?%s' % urllib.urlencode( params ) )
        result   = response.read()
        parts    = result.split( '=' )
        if len( parts ) == 2 and parts[0] == 'access_token':
            self.access_token = parts[1]

    def get_params(self, **kw):
        self.json_response = kw.pop('json_response', True)
        params = {}
        if self.access_token:
            params['access_token'] = self.access_token
        params.update(kw)
        return params

    def prepare_response(self, response):
        if self.json_response:
            response = json.loads(response)
        return response

    def get(self, path, **kw):
        params = self.get_params(**kw)
        if not path.startswith('http:') and not path.startswith('https:'):
            url = '%s%s?%s' % (self.BASE_URL, path, urllib.urlencode(params))
        else:
            url = path
        logger.info('fetching url: %s', url)
        return self.prepare_response(urllib2.urlopen(url).read())

    def post(self, path, **kw):
        params = self.get_params(**kw)
        url = self.BASE_URL + path
        data = urllib.urlencode(params)
        return self.prepare_response(urllib2.urlopen(url, data).read())

    def delete(self, path, **kw):
        params = self.get_params(**kw)
        url = self.BASE_URL + path
        request = urllib2.Request(url, data=urllib.urlencode(params))
        request.get_method = lambda:'DELETE'
        return self.prepare_response(urllib2.urlopen(request).read())

    def renew_access_token(self, app_id, app_secret):
        import cgi
        resp = self.get('/oauth/access_token',
                grant_type='fb_exchange_token',
                client_id=app_id,
                client_secret=app_secret,
                fb_exchange_token=self.access_token,
                json_response=False,
        )
        resp = dict(cgi.parse_qsl(resp))
        self.access_token = resp.get('access_token')
        return self.access_token

    renew_token = renew_access_token

    def code_to_access_token(self, code, app_id, app_secret, redirect_uri=''):
        import cgi
        resp = self.get('/oauth/access_token',
                client_id=app_id,
                client_secret=app_secret,
                redirect_uri=redirect_uri,
                code=code,
                json_response=False,
        )
        resp = dict(cgi.parse_qsl(resp))
        self.access_token = resp.get('access_token')
        return self.access_token

