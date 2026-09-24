# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

`filmaster-common` is the `film_common` package, a helper library for the Django projects of
Filmaster: cache-key conventions, Redis helpers, JSON model fields, a management-command base,
thread-local request access, locking, JSON-RPC and Facebook Graph clients, and a few small
Django apps.

## History

The history up to `ec29525` ("added admin.py, cleanup", 2015) was converted from the original
Mercurial repository, which lived on Bitbucket until Mercurial hosting there was shut down in
2020. Branch `stable` is the old Mercurial branch of that name, last merged in 2014, and not a
line of work to build on.

## Environment

Python 2.7 and Django 1.8; write code in that idiom. There is no build, lint or test command
that runs on its own: the package is only importable inside a configured Django project,
because many modules read `django.conf.settings` at import time. `setup.py` declares only
`pytz` and `jsonrpclib`. The other imports come from the host project: Django, `redis`,
`piston` (`utils.api`), `celery` (`tasks`), `nose` (`utils.test`), `sorl-thumbnail`
(`utils.thumbnails`) and `requests` (`utils.alerts`).

## Django apps

Three packages have models, and each has to be listed in `INSTALLED_APPS` separately:

- `film_common` — `RedisCacheDumps`, a key → pickled blob table, with
  `save_pickled_to_db` / `load_pickled_from_db`, plus the `alerts` and `collectstaticfast`
  management commands.
- `film_common.utils.db.settings` — `Settings`, a namespaced key/value store with admin.
  `Settings.get` reads through the Django cache and a `post_save` handler refreshes it.
- `film_common.utils.locking` — `Lock`, the table behind `acquire_lock_db`.

**Their `migrations/` packages are South migrations, not Django ones.** Django 1.7+ detects
the failed `south` import and treats all three apps as unmigrated: their tables are created by
`migrate`'s syncdb step, and schema changes to these models are not applied to an existing
database.

## Modules

- `management.base.BaseCommand` — management-command base that activates
  `settings.LANGUAGE_CODE` and maps `--verbosity` to the console log level
  (`utils.log.set_verbosity_level`).
- `utils.cache` — the `Key(prefix, *args)` cache-key convention and `get`/`set`/`delete`/
  `cache_query`/`cache_func`, with TTL constants and `CACHE_TIMEOUTS`. `Key` formats models
  by pk, users by username, querysets/lists/dicts recursively, and hashes keys over 230
  chars. Per-prefix options (`timeout`, `is_common`, `version`) come from
  `settings.CACHE_PREFIXES`; `CACHE_MIDDLEWARE_KEY_PREFIX` namespaces every key not marked
  common. With `CAN_SKIP_CACHE`, a `?nocache` request from a user with `can_skip_cache`
  forces misses.
- `utils.db.fields` — `JSONField` / `DictField` (`SubfieldBase` text fields). `DictField`
  defaults to the literal string `u"{}"` and skips serialisation for it.
- `utils.db.FieldChangeDetectorMixin` — model mixin that snapshots `DETECT_CHANGE_FIELDS` on
  load and answers `has_field_changed` / `prev_value`.
- `base_models.RedisSyncable` — abstract model with `updated_at` / `sync_source` /
  `is_deleted`. Its metaclass registers every subclass by name in `_subclasses`, and
  `change_log` (`ChangeLogManager`) pages through rows by an `"updated_at|pk"` sync mark,
  holding back the last `SYNC_DELAY` seconds. Subclasses implement `to_changelog`.
- `middleware.threadlocals` — the `ThreadLocals` middleware and `get_request()` /
  `get_current_user()`. It stores the request rather than the user, so reading it does not
  touch the session.
- `utils.redis_intf` — a lazy module-level `redis` connection, ratings and feature storage in
  Redis hashes and sets, pickle helpers, `RedisKeys` (class decorator generating key getters)
  and a Redis-backed `acquire_lock`.
- `utils.locking` — `single_instance_task` decorator; the lock class comes from
  `settings.ACQUIRE_LOCK_PROVIDER` (a dotted path such as
  `film_common.utils.redis_intf.acquire_lock`) and falls back to a no-op lock.
- `utils.importlib` — `autodiscover(module)` imports `<app>.<module>` from every installed
  app; `import_object` resolves a dotted path.
- Smaller helpers: `utils.log` (`AdminEmailHandler`, `ColoredFormatter`), `utils.apps.BaseApp`
  (configurable app with URL namespace, overridden by `<NAME>_CONFIG` settings),
  `utils.jsonrpc`, `utils.services`, `utils.fb`, `utils.api` (piston pagination and JSON
  emitter), `utils.alerts` (Graphite threshold alerts), `utils.progress`, `utils.uuids`,
  `utils.json_tools`, `utils.xml_tools`, `utils.list_wrapper`, `utils.dict_merger`,
  `utils.forms`, `utils.views`, `utils.profiling`, `sendmail`, `signals`, `constants`.

## Settings the library reads

| setting | used by |
| --- | --- |
| `CACHE_PREFIXES`, `CACHE_MIDDLEWARE_KEY_PREFIX`, `CAN_SKIP_CACHE` | `utils.cache` |
| `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, `REDIS_UNIX_SOCKET`, `REDIS_PASSWORD`, `REDIS_PREFIXES_TO_REMOVE` | `utils.redis_intf` |
| `USE_REDIS`, `DOMAIN`, `INTEGRATION_TESTS` | `utils.test` |
| `ACQUIRE_LOCK_PROVIDER`, `SECRET_KEY` | `utils.locking` |
| `LANGUAGE_CODE` | `management.base` |
| `TIME_ZONE` | `utils.uuids`, at import |
| `STATICFILES_STORAGE` | `utils.thumbnails` (at import), `collectstaticfast` |
| `PROFILING_ENABLED` | `utils.profiling`, at import |
| `GRAPHITE_URL` | `utils.alerts` |
| `INTERNAL_IPS` | `utils.log` |

## Traps

- `utils.redis_intf.create_redis_connection` reads `REDIS_UNIX_SOCKET` and `REDIS_PASSWORD`
  with a one-argument `getattr`, so the connection raises `AttributeError` under any settings
  module that does not define both (`None` is enough). The connection is a
  `SimpleLazyObject`, so this fires on first use of `redis_intf.redis`, not on import.
  Opening it also writes `settings.MAX_REDIS_MEMORY_USAGE`.
- `utils/cache_in_redis.py` imports `recommendation_service.stats`, a module that is neither
  here nor a dependency, so it and `tasks.dump_cache` (which imports it lazily) cannot run.
- `utils/test.py` imports `django.test.simple`, removed in Django 1.6, so `TestCase`,
  `TestRunner` and everything importing them fail to import — including the tests in
  `film_common/tests/`.
