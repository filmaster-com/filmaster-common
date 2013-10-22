from piston.emitters import Emitter, DateTimeAwareJSONEncoder
from piston.validate_jsonp import is_valid_jsonp_callback_value
from django.utils import simplejson

API_PAGE_SIZE = 10

def _int_param(request, name, default):
    try:
        return int(request.GET.get(name, default))
    except ValueError, e:
        return default

def paginated_collection(request, object_list, wrap_func=lambda x:x, default_limit=API_PAGE_SIZE):
    limit = _int_param(request, 'limit', default_limit)
    page_nr = _int_param(request, 'page', 1)

    object_list = list(object_list[(page_nr - 1) * limit:page_nr * limit + 1])
    has_next = len(object_list) > limit
    if has_next:
        del object_list[-1]

    if not object_list and page_nr > 1:
        from django.http import Http404
        raise Http404

    from urllib import urlencode

    if has_next:
        next_params = request.GET.copy()
        next_params['page'] = page_nr + 1
        next_uri = "%s?%s" % (request.META['PATH_INFO'], urlencode(next_params.items()))
    else:
        next_uri = None

    if page_nr>1:
        prev_params = request.GET.copy()
        prev_params['page'] = page_nr - 1
        prev_uri = "%s?%s" % (request.META['PATH_INFO'], urlencode(prev_params.items()))
    else:
        prev_uri = None
        
    return {
        'objects':list(wrap_func(i) for i in object_list),
        'paginator': {
            'page': page_nr,
            'next_uri': next_uri,
            'prev_uri': prev_uri,
        }
    }

def collection(request, object_list, wrap_func = lambda x:x):
    return {
        'objects':list(wrap_func(i) for i in object_list),
    }

class JSONEmitter(Emitter):
    """
    JSON emitter, understands timestamps.
    """
    def render(self, request):
        cb = request.GET.get('callback', None)
        try:
            indent = int(request.GET.get('indent',2))
        except:
            indent = None

        seria = simplejson.dumps(self.construct(), cls=DateTimeAwareJSONEncoder, ensure_ascii=False, indent=indent)

        # Callback
        if cb and is_valid_jsonp_callback_value(cb):
            return '%s(%s)' % (cb, seria)

        return seria

Emitter.register('json', JSONEmitter, 'application/json; charset=utf-8')
