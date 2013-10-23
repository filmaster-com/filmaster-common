import jsonrpclib
import types
import traceback

from jsonrpclib import Fault
import jsonrpclib.jsonrpc
import SimpleXMLRPCServer

from film_common.utils import json_tools

import logging
logger = logging.getLogger(__name__)

jsonrpclib.config.use_jsonclass = False

# monkey patch jsonrpclib to allow encoding of custom objects
jsonrpclib.jsonrpc.jdumps = json_tools.dumps
jsonrpclib.jsonrpc.jloads = json_tools.loads

class Service(object):

    @classmethod
    def from_request(cls, request):
        """
            creates Service object from request
        """
        return cls()

    def _dispatch(self, method, params):
        """
        overwritten for better debugging
        """
        logger.debug('calling %s %r', method, params)
        self.last_method = method
        try:
            func = SimpleXMLRPCServer.resolve_dotted_attribute(
                self,
                method,
                True
                )
        except AttributeError:
            func = None

        if func is not None:
            try:
                if type(params) is types.ListType:
                    response = func(*params)
                else:
                    response = func(**params)
                return response
            except TypeError:
                logger.exception('rpc dispatch exception')
                return Fault(-32602, 'Invalid parameters.')
            except:
                logger.exception('rpc dispatch exception')
                err_lines = traceback.format_exc().splitlines()
                trace_string = '%s | %s' % (err_lines[-3], err_lines[-1])
                fault = jsonrpclib.Fault(-32603, 'Server error: %s' %
                                         trace_string)
                return fault
        else:
            return Fault(-32601, 'Method %s not supported.' % method)
