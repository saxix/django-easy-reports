import hashlib
from operator import itemgetter
from django.core.cache import cache as _cache
from django.db.models.signals import post_save, post_delete
from ereports.utils import fqn, flatten


EREPORTS_CACHE_MODELS_PREFIX = 'ereports/models/%s'


def invalidate(sender, **kwargs):
    try:
        _cache.incr(EREPORTS_CACHE_MODELS_PREFIX % fqn(sender), 1)
    except ValueError:
        reset(sender)


def reset(model, **kwargs):
    _cache.set(EREPORTS_CACHE_MODELS_PREFIX % fqn(model), 0)


def monitor_model(model):
    version = _cache.get(EREPORTS_CACHE_MODELS_PREFIX % fqn(model))
    if version is None:
        reset(model)
    post_save.connect(invalidate, sender=model, dispatch_uid="ereports_save_%s" % str(model))
    post_delete.connect(invalidate, sender=model, dispatch_uid="ereports_delete_%s" % str(model))


class BaseCacheManager(object):
    def store(self, key, value, timeout=None, version=None):
        _cache.set(key, value, timeout, version)

    def retrieve(self, cache_key, default=None, version=None):
        return _cache.get(cache_key, default, version)

    def delete(self, cache_key, version=None):
        return _cache.delete(cache_key, version)

    def get_last_cache_version(self, model):
        return _cache.get(EREPORTS_CACHE_MODELS_PREFIX % fqn(model), 0)

    def get_model_gen_part(self, model):
        """
            returns a tuple composed by 'generation prefix', 'generation value'
            fro the passed model

        :param model:
        :return:
        """
        prefix = fqn(model)
        return prefix, self.get_last_cache_version(model)

    def get_key(self, target):
        raise NotImplementedError()


class DummyCacheManager(BaseCacheManager):
    def store(self, key, value, timeout=None, version=None):
        pass

    def retrieve(self, cache_key, default=None, version=None):
        return None

    def delete(self, cache_key, version=None):
        return None

    def get_key(self, target):
        return ''


class DatasourceCacheManager(BaseCacheManager):
    def get_key(self, datasource):
        parts = [self.get_model_gen_part(datasource.model)]

        if datasource.dependent_models:
            for model in datasource.dependent_models:
                parts.append(self.get_model_gen_part(model))

        parts = sorted(parts, key=itemgetter(0))
        parts.insert(0, ('ereports', _cache.get('ereports', 1)))  # to invalidate whole ereports cache

        m = hashlib.md5()
        m.update("{0}-{1}-{2}-{3}".format(str(datasource.columns), str(datasource.kwfilters),
                                          str(datasource.filters), str(datasource.order_by)))
        parts.append(m.hexdigest())
        key = "/".join(map(str, flatten(parts)))

        return key
