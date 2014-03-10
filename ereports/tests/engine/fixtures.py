from django.db.models.query import EmptyQuerySet, QuerySet


class FakeQuerySet(QuerySet):
    """Turn a list into a Django QuerySet... kind of."""

    def __init__(self, model=None, query=None, using=None, items=None):
        super(FakeQuerySet, self).__init__(model, query, using)
        self._result_cache = items or []

    def count(self):
        return len(self)

    def _clone(self, klass=None, setup=False, **kwargs):
        return FakeQuerySet(self.model, items=self._result_cache)
