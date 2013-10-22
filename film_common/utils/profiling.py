"""This is profiling utility, it provides 'profile_me' decorator,
   after execution of program it dumps all collected stats to file.
   TODO(janek): switching profiling off by settings
"""
import cProfile
import datetime
import atexit
from inspect import getmodule
from collections import defaultdict

from django.conf import settings

PROFILERS = defaultdict(cProfile.Profile)


def _fun_name(fun):
    return getmodule(fun).__name__ + '.' + fun.__name__


if settings.PROFILING_ENABLED:
    def profile_me(fun):
        """Decorator for function to be profiled."""
        prof = PROFILERS[_fun_name(fun)]
        return lambda *args, **kwargs: prof.runcall(fun, *args, **kwargs)
else:
    def profile_me(fun):
        return fun


def dump_stats():
    """Dumps profilng informations to files in folder profiling_statistics.
    """
    filename_template = 'profiling_statistics/%s.py_profile'
    now = datetime.datetime.now()
    now_str = now.strftime('%y.%m.%d.%H.%M.%S')
    for name, profiler in PROFILERS.items():
        if profiler.getstats():
            profiler.dump_stats(filename_template % (name + '@' + now_str))


if settings.PROFILING_ENABLED:
    atexit.register(dump_stats)
