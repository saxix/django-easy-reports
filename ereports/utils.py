# -*- coding: utf-8 -*-
from importlib import import_module
from inspect import isclass
from logging import getLogger
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.encoding import smart_str
from six import string_types


logger = getLogger(__name__)


def get_model_field_names(model):
    return [f.name for f in model._meta.fields]


def currencyformat(value, thousand_sep=',', decimal_sep='.'):
    """
    Returns the currency format of the value param using specified separators

    Usage: {% value_to_format|currencyformat %}
    """
    sign = {False: '-', True: ''}[value > 0]
    integer_part_string = str(abs(int(value)))
    f = lambda x, y, list=[]: f(x[:-y], y, [(x[-y:])] + list) if x else list
    integer_part = thousand_sep.join(f(integer_part_string, 3))
    return "%s%s%s%s" % (sign, integer_part, decimal_sep, ("%0.2f" % value)[-2:])


def fqn(o):
    """Returns the fully qualified class name of an object or a class

    >>> import pytest
    >>> with pytest.raises(ValueError):
    ...    fqn('hello')

    >>> fqn(fqn)
    'ereports.utils.function'

    >>> class FakeClass():
    ...    pass
    >>> fqn(FakeClass)
    'ereports.utils.FakeClass'

    :param o: object or class
    :return: class name
    """
    parts = []
    if not hasattr(o, '__module__'):
        raise ValueError('Invalid argument `%s`' % o)
    parts.append(o.__module__)
    if isclass(o):
        parts.append(o.__name__)
    else:
        parts.append(o.__class__.__name__)
    return ".".join(parts)


def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:

    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]

    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, (8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""

    result = []
    for el in x:
        # if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, string_types):
            result.extend(flatten(el))
        else:
            result.append(el)
    return list(result)


def get_verbose_name(model_or_queryset, field_path):
    """
        returns the verbose name of a Field.

        Examples:

        >>> import pytest
        >>> class Fake(models.Model):
        ...     user = models.CharField(verbose_name='user', max_length=30)
        >>> get_verbose_name(Fake(), 'user')
        'user'
        >>> get_verbose_name(Fake, 'user')
        'user'
        >>> with pytest.raises(AttributeError):
        ...     get_verbose_name(Fake, 'wrong') # doctest: +IGNORE_EXCEPTION_DETAIL, +ELLIPSIS

    :param model_or_queryset: can be a Model/Manager or Queryset
    :param field_path: dotted path to rhe field name
    :return: verbose_name attrinute of Field
    """

    model = getattr(model_or_queryset, 'model', model_or_queryset)
    field = get_field_from_path(model, field_path)
    if field and hasattr(field, 'verbose_name'):
        label = field.verbose_name
    elif field:
        label = field.name.replace('.', ' ').replace('_', ' ')
    else:
        raise AttributeError(field_path)
    return smart_str(label)


def get_field_from_path(Model, field_path):
    """
    get a Model and a path to a attribute, return the field object

    a = get_field_from_path(Model, 'fk.fk.fieldname')
    """
    parts = field_path.split('.')
    target = parts[0]
    if target in Model._meta.get_all_field_names():
        field_object, __, __, __ = Model._meta.get_field_by_name(target)
        if isinstance(field_object, models.fields.related.ForeignKey):
            if parts[1:]:
                return get_field_from_path(field_object.rel.to, '.'.join(parts[1:]))
            else:
                return field_object
        else:
            return field_object
    return None


def get_attr(obj, attr, default=None):
    """Recursive get object's attribute. May use dot notation.

    >>> class C(object): pass
    >>> a = C()
    >>> a.b = C()
    >>> a.b.c = 4
    >>> get_attr(a, 'b.c')
    4

    >>> get_attr(a, 'b.c.y', None)

    >>> get_attr(a, 'b.c.y', 1)
    1
    """
    if '.' not in attr:
        return getattr(obj, attr, default)
    else:
        L = attr.split('.')
        return get_attr(getattr(obj, L[0], default), '.'.join(L[1:]), default)


class StartWithList(list):
    """List redefined to check list items start with particular string

    >>> l = StartWithList(['123', '231', '321'])
    >>> '1' in l
    True
    >>> '23' in l
    True
    >>> '321' in l
    True
    >>> '21' in l
    False
    >>> '4' in l
    False
    """
    def __contains__(self, y):
        for el in self:
            if el.startswith(y):
                return True
        return False


def filter_dictionary(dictionary, filter_func):
    """
        returns the first element of `dictionary` where the element's key pass the filter_func.

        filter_func can be either a callable or a value.
        - if callable filtering is checked with `test(element_value)`
        - if value filtering is checked with `element_value == filter_func`

    :param dictionary:
    :param test:
    :return:

    >>> filter_dictionary({'arg': 'test'}, 'test')
    'arg'
    >>> filter_dictionary({}, 'test')

    >>> def is_test(value):
    ...    return value == 'test'
    >>> filter_dictionary({'arg': 'test'}, is_test)
    'arg'
    """
    if not callable(filter_func):
        test_func = lambda x: x == filter_func
    else:
        test_func = filter_func
    for key, value in dictionary.iteritems():
        if test_func(value):
            return key


def import_by_path(dotted_path, error_prefix=''):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImproperlyConfigured if something goes wrong.

    >>> import pytest
    >>> from django.contrib.auth.models import User
    >>> from django.core.exceptions import ImproperlyConfigured
    >>> with pytest.raises(ImproperlyConfigured):
    ...    import_by_path("wrongpath")

    >>> with pytest.raises(ImproperlyConfigured):
    ...    import_by_path("wrong.path")

    >>> with pytest.raises(ImproperlyConfigured):
    ...    import_by_path("django.contrib.auth.models.Wrong")

    >>> cls = import_by_path("django.contrib.auth.models.User")
    >>> assert isinstance(cls(), User)
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        raise ImproperlyConfigured("%s%s doesn't look like a module path" % (
            error_prefix, dotted_path))
    try:
        module = import_module(module_path)
    except ImportError as e:
        raise ImproperlyConfigured('%sError importing module %s: "%s"' % (
            error_prefix, module_path, e))
    try:
        attr = getattr(module, class_name)
    except AttributeError:
        raise ImproperlyConfigured('%sModule "%s" does not define a "%s" attribute/class' % (
            error_prefix, module_path, class_name))
    return attr
