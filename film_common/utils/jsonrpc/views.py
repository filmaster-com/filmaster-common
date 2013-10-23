from django.views.generic.base import View
from django import http
from .service import jsonrpclib # forces monkey patching jsonrpclib
from jsonrpclib.SimpleJSONRPCServer import SimpleJSONRPCDispatcher

import logging
logger = logging.getLogger(__name__)

class RPCHandler(View):

    @classmethod
    def as_view_for(cls, service_class, **kw):
        class _RPCHandler(cls):
            SERVICE_CLASS = service_class
        return _RPCHandler.as_view(**kw)

    def post(self, *args, **kw):
        dispatcher = SimpleJSONRPCDispatcher()
        service = self.SERVICE_CLASS.from_request(self.request)
        dispatcher.register_instance(service)
        out = dispatcher._marshaled_dispatch(self.request.raw_post_data)
        return http.HttpResponse(out, mimetype='application/json')

    def dispatch(self, *args, **kw):
        try:
            return super(RPCHandler, self).dispatch(*args, **kw)
        except:
            logger.exception('rpc')
            raise

