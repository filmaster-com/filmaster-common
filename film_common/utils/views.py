from django import http
from django.template import RequestContext
from django.template.loader import render_to_string
from base64 import b64decode
import re

class BasicAuthMixin(object):
    AUTH_USER_PASS = None
    ACCESS_DENIED_TEMPLATE = None

    def dispatch(self, request, *args, **kw):
        if not self._check_auth(request):
            return self._access_denied_response(request)
        return super(BasicAuthMixin, self).dispatch(request, *args, **kw)

    def is_auth_enabled(self):
        return bool(self.AUTH_USER_PASS)

    def check_credentials(self, credentials):
        return credentials == self.AUTH_USER_PASS

    def _access_denied_response(self, request):
        if self.ACCESS_DENIED_TEMPLATE:
            out = render_to_string(
                self.ACCESS_DENIED_TEMPLATE,
                context_instance=RequestContext(request),
            )
        else:
            out = "Access Denied"
        response = http.HttpResponse(out, status=401)
        response['WWW-Authenticate'] = 'Basic realm="Filmaster beta"'
        return response

    def _check_auth(self, request):
        if not self.is_auth_enabled():
            return True
        if hasattr(request, 'session') and request.session.get('allowed_%s' % self.auth_allowed_session_key()):
            return True
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Basic '):
            return False

        cred = b64decode(auth_header[6:].strip())
        allowed = self.check_credentials(cred)
        if allowed and hasattr(request, 'session'):
            request.session['allowed_%s' % self.auth_allowed_session_key()] = True
        return allowed

    def auth_allowed_session_key(self):
        return self.__class__.__name__
