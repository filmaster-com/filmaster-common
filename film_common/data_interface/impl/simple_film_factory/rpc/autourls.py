from django.conf.urls.defaults import *
from film_common.utils.jsonrpc.views import RPCHandler
from ..factory import SimpleDisplayableFilmFactory

urlpatterns = patterns('',
    url('^rpc/simple-film-factory/', RPCHandler.as_view_for(SimpleDisplayableFilmFactory)),
)
